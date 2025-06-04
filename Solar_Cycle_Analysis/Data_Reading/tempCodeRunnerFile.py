for col in df.select_dtypes(include=[np.number]).columns:# filter out bad data
    #     df[col] = df[col].apply(lambda x: np.nan if np.isclose(x, -1.0e31) else x)