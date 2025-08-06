from ydata_profiling import ProfileReport

def generate_profile(df, name="report", output="reports/profile.html"):
    profile = ProfileReport(df, title=f"{name} Data Profile", explorative=True)
    profile.to_file(output)
    print(f"📄 Profile report saved to {output}")
