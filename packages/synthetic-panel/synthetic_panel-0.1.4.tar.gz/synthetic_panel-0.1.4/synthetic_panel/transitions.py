import os
import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal
import statsmodels.formula.api as smf
from tqdm import tqdm
from joblib import Parallel, delayed
import time
from contextlib import contextmanager
import joblib

# ETA formatter
def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f} sec"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} min"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hr"
    else:
        return f"{seconds / 86400:.1f} days"

# tqdm-joblib wrapper for multiprocessing progress
@contextmanager
def tqdm_joblib(tqdm_object):
    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_callback
        tqdm_object.close()

def estimate_transitions(
    df_round1,
    df_round2,
    x_cols,
    cohort_cols,
    dep_var_round1,
    dep_var_round2,
    pline_round1_name='pline_7',
    pline_round2_name='pline',
    cohort_col='cohort',
    log_transform=True,
    use_weights=None,
    weight_round2='weight2',
    auto_create_cohort=True,
    n_bootstrap=1000,
    use_multiprocessing=False,
    output_excel_filename=None,
    seed=1
):
    np.random.seed(seed)

    df_round1 = df_round1.copy()
    df_round2 = df_round2.copy()
    
    # Rename dep_var_round2 to 'pcep' if needed
    if dep_var_round2 != 'pcep':
        if dep_var_round2 in df_round2.columns:
            df_round2 = df_round2.rename(columns={dep_var_round2: 'pcep'})
        else:
            raise ValueError(f"dep_var_round2 '{dep_var_round2}' not found in df_round2 columns")
        dep_var_round2 = 'pcep'

    # Convert cohort key columns to integer dtype if not already
    for col in x_cols:
        changed = False
        if col in df_round1.columns and not pd.api.types.is_integer_dtype(df_round1[col]):
            df_round1[col] = df_round1[col].astype(int)
            changed = True
        if col in df_round2.columns and not pd.api.types.is_integer_dtype(df_round2[col]):
            df_round2[col] = df_round2[col].astype(int)
            changed = True
        if changed:
            print(f"⚠️ Column '{col}' was not integer and has been converted to int.")
        else:
            print(f"✅ Column '{col}' is already integer.")
    
    # Set transition weights for df_round2
    if use_weights:
        df_round2['trans_weight'] = df_round2[weight_round2] / df_round2[weight_round2].sum()
    else:
        df_round2['trans_weight'] = 1

    # Log transform dependent variables and poverty lines if specified
    if log_transform:
        df_round1[dep_var_round1] = np.log(df_round1[dep_var_round1])
        df_round2[dep_var_round2] = np.log(df_round2[dep_var_round2])
        df_round1[pline_round1_name] = np.log(df_round1[pline_round1_name])
        df_round2[pline_round2_name] = np.log(df_round2[pline_round2_name])

    # Auto-generate cohort column by concatenating cohort_cols as strings
    if auto_create_cohort:
        print(f"\n🔧 Auto-generating cohort from cohort_cols: {cohort_cols}")
        for col in cohort_cols:
            df_round1[f"{col}_str"] = df_round1[col].astype(str)
            df_round2[f"{col}_str"] = df_round2[col].astype(str)
        cohort_str_cols = [f"{col}_str" for col in cohort_cols]
        df_round1[cohort_col] = df_round1[cohort_str_cols].agg('_'.join, axis=1)
        df_round2[cohort_col] = df_round2[cohort_str_cols].agg('_'.join, axis=1)

    # Warn if any cohort has fewer than 100 observations in round2
    cohort_counts = df_round2[cohort_col].value_counts()
    small_cohorts = cohort_counts[cohort_counts < 100]
    if not small_cohorts.empty:
        print("\n  WARNING: The following cohorts have fewer than 100 observations in df_round2:\n")
        print(small_cohorts)
        print("\nConsider collapsing categories or using fewer cohort_cols.")
    else:
        print(f"\n  All {len(cohort_counts)} cohorts have at least 100 observations.")

    # Compute average poverty line in round1 by cohort, merge to round2
    pline_round1_by_cohort = df_round1.groupby(cohort_col)[pline_round1_name].mean().reset_index(name='pline_round1_avg')
    df_round2 = df_round2.merge(pline_round1_by_cohort, on=cohort_col, how='left')
    pline_round1_col = 'pline_round1_avg'

    # Define transition signs for each transition type
    transitions = {
        'Stayed Poor (P11)': (1, 1),
        'Escaped Poverty (P10)': (1, -1),
        'Fell into Poverty (P01)': (-1, 1),
        'Stayed Non-poor (P00)': (-1, -1)
    }

    # Regression formulas without intercept
    formula_round1 = f"{dep_var_round1} ~ {' + '.join(x_cols)} - 1"
    formula_round2 = f"{dep_var_round2} ~ {' + '.join(x_cols)} - 1"

    # Fit OLS models
    model_round1 = smf.ols(formula_round1, data=df_round1).fit()
    model_round2 = smf.ols(formula_round2, data=df_round2).fit()

    coeffs_round1 = model_round1.params[x_cols].values
    coeffs_round2 = model_round2.params[x_cols].values

    resid_std_round1 = np.sqrt(model_round1.mse_resid)
    resid_std_round2 = np.sqrt(model_round2.mse_resid)

    cov_matrix = df_round2[x_cols].cov().values

    # Single bootstrap iteration function
    def run_iteration(_):
        sample_df = df_round2.sample(n=len(df_round2), replace=True)

        sample_df['yhat_round1'] = model_round1.predict(sample_df)
        sample_df['yhat_round2'] = model_round2.predict(sample_df)

        round1_cohort_mean = df_round1.groupby(cohort_col)[dep_var_round1].mean().reset_index()
        round2_cohort_mean = sample_df.groupby(cohort_col)[dep_var_round2].mean().reset_index()
        df_cohort = pd.merge(round1_cohort_mean, round2_cohort_mean, on=cohort_col)

        rho_c = df_cohort[dep_var_round1].corr(df_cohort[dep_var_round2])
        ystd_round1 = df_round1[dep_var_round1].std()
        ystd_round2 = sample_df[dep_var_round2].std()

        mm = coeffs_round1.T @ cov_matrix @ coeffs_round2
        rho_partial = np.clip(
            (rho_c * ystd_round1 * ystd_round2 - mm) / (resid_std_round1 * resid_std_round2),
            -0.9999, 0.9999
        )

        probs_dict = {}
        for name, (d1, d2) in transitions.items():
            probs = [
                multivariate_normal.cdf(
                    [
                        d1 * (pline1 - yhat1) / resid_std_round1,
                        d2 * (pline2 - yhat2) / resid_std_round2
                    ],
                    mean=[0, 0],
                    cov=[[1, d1 * d2 * rho_partial], [d1 * d2 * rho_partial, 1]]
                )
                for yhat1, yhat2, pline1, pline2 in zip(
                    sample_df['yhat_round1'],
                    sample_df['yhat_round2'],
                    sample_df[pline_round1_col],
                    sample_df[pline_round2_name]
                )
            ]
            probs_dict[name] = np.average(probs, weights=sample_df['trans_weight'])

        # Marginal probabilities at t=1
        p11 = probs_dict['Stayed Poor (P11)']
        p10 = probs_dict['Escaped Poverty (P10)']
        p01 = probs_dict['Fell into Poverty (P01)']
        p00 = probs_dict['Stayed Non-poor (P00)']

        p_poor_t1 = p11 + p10
        p_nonpoor_t1 = p01 + p00

        # Conditional transition probabilities
        cond_p11 = p11 / p_poor_t1 if p_poor_t1 > 0 else np.nan
        cond_p10 = p10 / p_poor_t1 if p_poor_t1 > 0 else np.nan
        cond_p01 = p01 / p_nonpoor_t1 if p_nonpoor_t1 > 0 else np.nan
        cond_p00 = p00 / p_nonpoor_t1 if p_nonpoor_t1 > 0 else np.nan

        return {
            'rho_c': rho_c,
            'rho_partial': rho_partial,
            **probs_dict,
            'cond_Stayed Poor (P11)': cond_p11,
            'cond_Escaped Poverty (P10)': cond_p10,
            'cond_Fell into Poverty (P01)': cond_p01,
            'cond_Stayed Non-poor (P00)': cond_p00
        }

    print("\n⏳ Running bootstrap...")
    start_time = time.time()

    if use_multiprocessing:
        with tqdm_joblib(tqdm(total=n_bootstrap, desc="Bootstrap (MP)", unit="iter")):
            results = Parallel(n_jobs=-1)(delayed(run_iteration)(i) for i in range(n_bootstrap))
    else:
        results = []
        for i in range(n_bootstrap):
            results.append(run_iteration(i))
            if (i + 1) % 50 == 0 or i == n_bootstrap - 1:
                elapsed = time.time() - start_time
                avg_time = elapsed / (i + 1)
                eta = avg_time * (n_bootstrap - (i + 1))
                print(f"Completed {i + 1}/{n_bootstrap} - ETA: {format_duration(eta)}", end='\r')

    end_time = time.time()

    bootstrap_df = pd.DataFrame(results)

    print("\n✅ Bootstrap completed.")
    print(f"⏱️  Total time: {format_duration(end_time - start_time)}")

    # Print joint probabilities (transition shares)
    print("\n=== Bootstrap Poverty Transition Shares (Joint Probabilities) ===")
    for name in transitions:
        mean = bootstrap_df[name].mean()
        se = bootstrap_df[name].std(ddof=1)
        print(f"{name}: {mean*100:.1f}%  (SE: {se*100:.2f}%)")

    # Print conditional probabilities
    print("\n=== Bootstrap Conditional Transition Probabilities ===")
    cond_names = [
        'cond_Stayed Poor (P11)',
        'cond_Escaped Poverty (P10)',
        'cond_Fell into Poverty (P01)',
        'cond_Stayed Non-poor (P00)'
    ]
    for name in cond_names:
        mean = bootstrap_df[name].mean()
        se = bootstrap_df[name].std(ddof=1)
        print(f"{name}: {mean*100:.1f}%  (SE: {se*100:.2f}%)")

    if output_excel_filename:
        full_output_path = os.path.join(os.getcwd(), output_excel_filename)
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        bootstrap_df.to_excel(full_output_path, index=False)
        print(f"\n💾 Saved results to {full_output_path}")

    return bootstrap_df
