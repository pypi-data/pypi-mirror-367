import pycountry

KNOWN_COUNTRIES ={country.alpha_2 for country in pycountry.countries}

def test_no_null_purchase_amount(sample_df):
    assert sample_df["purchase_amount"].notnull().all()

def test_known_country_codes(sample_df):
    assert set(sample_df["country_code"]).issubset(KNOWN_COUNTRIES)

def test_unique_purchase_ids(sample_df):
    assert sample_df["purchase_id"].is_unique

def test_revenue_not_negative(sample_df):
    assert (sample_df["purchase_amount"] >= 0).all()
