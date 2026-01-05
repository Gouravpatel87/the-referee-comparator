import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="The Referee: Cloud Comparator", layout="wide")
st.title("🧑‍⚖️ The Referee - Cloud Service Comparator")
st.markdown("""
**Week 6 AI for Bharat**  
Live AWS pricing fetched from **public AWS Price List API** (no credentials needed!).  
Balanced pros/cons + trade-offs to help you decide. Built fast with Kiro! 🚀
""")

# === Region Selector ===
region_options = ["US East (N. Virginia)", "Asia Pacific (Mumbai)", "EU (Ireland)"]
region_codes = ["us-east-1", "ap-south-1", "eu-west-1"]
region = st.sidebar.selectbox("AWS Region", region_options, index=0)
region_code = region_codes[region_options.index(region)]

# === Live Pricing Function (Safe with Fallback) ===
@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_live_prices(region_code):
    base_url = "https://pricing.us-east-1.amazonaws.com"
    try:
        offers_index = requests.get(f"{base_url}/offers/v1.0/aws/index.json", timeout=10).json()

        prices = {
            "lambda_request": 0.0000002,    # $0.20 per 1M requests
            "lambda_gb_s": 0.00001667,      # $0.00001667 per GB-second
            "s3_gb_month": 0.023,
            "efs_gb_month": 0.30,
            "ebs_gb_month": 0.10
        }

        # Helper to get offer data
        def get_offer_data(offer_name):
            url = base_url + offers_index['offers'][offer_name]['currentRegionIndexUrl']
            region_index = requests.get(url, timeout=10).json()
            version_url = region_index['regions'][region_code]['currentVersionUrl']
            return requests.get(base_url + version_url, timeout=10).json()

        # Lambda pricing
        lambda_data = get_offer_data('AWSLambda')
        for product in lambda_data['products'].values():
            attrs = product['attributes']
            if attrs.get('usagetype', '').endswith('Requests'):
                sku = product['sku']
                term = next(iter(lambda_data['terms']['OnDemand'][sku].values()))
                dim = next(iter(term['priceDimensions'].values()))
                prices["lambda_request"] = float(dim['pricePerUnit']['USD'])
            if 'Duration' in attrs.get('usagetype', ''):
                sku = product['sku']
                term = next(iter(lambda_data['terms']['OnDemand'][sku].values()))
                dim = next(iter(term['priceDimensions'].values()))
                prices["lambda_gb_s"] = float(dim['pricePerUnit']['USD'])

        # S3 Standard storage
        s3_data = get_offer_data('AmazonS3')
        for product in s3_data['products'].values():
            if product['attributes'].get('storageClass') == 'General Purpose':
                sku = product['sku']
                term = next(iter(s3_data['terms']['OnDemand'][sku].values()))
                dim = next(iter(term['priceDimensions'].values()))
                prices["s3_gb_month"] = float(dim['pricePerUnit']['USD'])
                break

        return prices

    except Exception:
        st.warning("Live pricing fetch failed (network/issue) — using latest known prices (Jan 2026).")
        return {
            "lambda_request": 0.0000002,
            "lambda_gb_s": 0.00001667,
            "s3_gb_month": 0.023,
            "efs_gb_month": 0.30,
            "ebs_gb_month": 0.10
        }

# Load prices
prices = fetch_live_prices(region_code)
st.sidebar.success(f"Prices loaded for {region} 🌐")

# === Mode Selection (MUST come AFTER prices) ===
mode = st.sidebar.selectbox(
    "Comparison Mode",
    ["Serverless Compute (Lambda vs GCP vs Azure)", "AWS Storage (S3 vs EFS vs EBS)"]
)

# === Serverless Compute Mode ===
if mode == "Serverless Compute (Lambda vs GCP vs Azure)":
    st.header("Serverless Compute Comparison")
    st.markdown("AWS Lambda • Google Cloud Functions • Azure Functions")

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_requests = st.number_input("Monthly Invocations", min_value=0, value=1_000_000, step=100_000)
    with col2:
        avg_duration_ms = st.number_input("Average Duration (ms)", min_value=1, value=500, step=100)
    with col3:
        memory_mb = st.selectbox("Memory (MB)", [128, 256, 512, 1024, 2048, 4096], index=2)

    # Calculations
    duration_s = avg_duration_ms / 1000
    gb_seconds = monthly_requests * (memory_mb / 1024) * duration_s

    # AWS (Live)
    aws_requests_cost = max(monthly_requests - 1_000_000, 0) * prices["lambda_request"]
    aws_compute_cost = max(gb_seconds - 400_000, 0) * prices["lambda_gb_s"]
    aws_total = aws_requests_cost + aws_compute_cost

    # GCP & Azure (approximate – no public live API like AWS)
    gcp_total = (monthly_requests * 0.0000004) + (gb_seconds * 0.0000025)
    azure_total = (max(monthly_requests - 1_000_000, 0) * 0.0000002) + (max(gb_seconds - 400_000, 0) * 0.000016)

    data = {
        "Feature": ["Est. Monthly Cost (USD)", "Cold Starts", "Max Timeout", "Ecosystem", "Pros", "Cons"],
        "AWS Lambda": [
            f"${aws_total:.4f}",
            "~100-500 ms",
            "15 min",
            "AWS-native",
            "Fast cold starts, deep AWS integration",
            "15-min limit"
        ],
        "Google Cloud Functions": [
            f"${gcp_total:.4f}",
            "~200-600 ms",
            "60 min",
            "Google ML/Data",
            "Longer runs, great for AI",
            "Higher request cost"
        ],
        "Azure Functions": [
            f"${azure_total:.4f}",
            "~300 ms–2 s",
            "10 min",
            "Microsoft stack",
            ".NET & enterprise focus",
            "Slower cold starts"
        ]
    }
    df = pd.DataFrame(data)
    st.table(df.set_index("Feature"))

    st.markdown("### Trade-offs")
    st.markdown("""
    - **AWS Lambda**: Best speed & integration if you're already on AWS.
    - **Google**: Choose for long-running or ML-heavy functions.
    - **Azure**: Ideal if your team uses Microsoft tools.
    """)

# === AWS Storage Mode ===
else:
    st.header("AWS Storage Comparison")
    st.markdown("S3 (Object) • EFS (File) • EBS (Block)")

    col1, col2 = st.columns(2)
    with col1:
        storage_gb = st.number_input("Storage Amount (GB)", min_value=1, value=1000, step=100)
    with col2:
        access_pattern = st.selectbox("Primary Access Pattern",
                                      ["Global/web (backups, media)", "Shared files (multiple apps)", "Low-latency (databases)"])

    s3_cost = storage_gb * prices["s3_gb_month"]
    efs_cost = storage_gb * prices["efs_gb_month"]
    ebs_cost = storage_gb * prices["ebs_gb_month"]

    data = {
        "Feature": ["Est. Monthly Cost (USD)", "Type", "Access", "Performance", "Best For", "Pros", "Cons"],
        "Amazon S3": [f"${s3_cost:.2f}", "Object", "HTTP/API", "High throughput", "Backups/media", "Cheapest, durable", "Not a filesystem"],
        "Amazon EFS": [f"${efs_cost:.2f}", "File (NFS)", "Multi-instance", "Elastic", "Shared data", "True shared FS", "Most expensive"],
        "Amazon EBS": [f"${ebs_cost:.2f}", "Block", "Single EC2", "Lowest latency", "Databases", "High IOPS", "Tied to EC2"]
    }
    df = pd.DataFrame(data)
    st.table(df.set_index("Feature"))

    st.markdown("### Trade-offs")
    st.markdown("""
    - **S3**: Cheapest for large, global, infrequently accessed data.
    - **EFS**: When multiple servers need shared file access.
    - **EBS**: Highest performance for databases or boot volumes.
    """)

st.sidebar.info("Public AWS Price List API | No login required")