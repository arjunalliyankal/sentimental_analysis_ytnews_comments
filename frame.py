import streamlit as st
import scrape as sc
import analysis as ana
import seaborn as sns
import matplotlib.pyplot as plt

st.header("Sentimental Analyzer for YT Comments")
str = st.text_input("Paste URL from Youtube")


import urllib.parse as urlparse
import re

def extract_video_id(str):
    """
    Extracts the YouTube video ID from almost any YouTube link format.
    Returns the ID (11 chars) or empty string if invalid.
    """
    url =str.strip()
    if not url:
        return ""

    # 1. If user already provided only the ID
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    parsed = urlparse.urlparse(url)

    # 2. Check query parameter ?v=VIDEOID
    query = urlparse.parse_qs(parsed.query)
    if "v" in query:
        vid = query["v"][0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            return vid

    # 3. Check youtu.be shortlinks
    # Example: https://youtu.be/GWW-iYj2tKA?si=xxxx
    path = parsed.path.lstrip("/")
    if parsed.netloc in ["youtu.be", "www.youtu.be"]:
        # first part of path is the video id
        vid = path.split("/")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            return vid

    # 4. Check embedded URLs like /embed/VIDEOID
    match = re.search(r"(?:embed|shorts)/([A-Za-z0-9_-]{11})", url)
    if match:
        return match.group(1)

    # 5. Last fallback: find any 11-char YouTube-looking pattern
    fallback = re.search(r"[A-Za-z0-9_-]{11}", url)
    if fallback:
        return fallback.group(0)

    return ""
    
def plot_sentiment_chart(sentiment_summary):
    
    plt.figure(figsize=(6, 4))
    
    # Bar chart (NO custom colors as required)
    plt.bar(sentiment_summary["Sentiment"], sentiment_summary["Count"])
    
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.title("Sentiment Distribution")
    plt.tight_layout()
    st.pyplot(plt)

ok = st.button("Analysis")
 
if ok:
    
    vdo_url=extract_video_id(str)    
    cleaned_comments =sc.main(vdo_url)
    df,sentiment_counts_test,sentiment_counts= ana.analyze_sentiment_from_variable(cleaned_comments)
    st.write(df)
    
    plot_sentiment_chart(sentiment_counts_test)
    st.write(sentiment_counts_test)
   
    
    if sentiment_counts_test['Count'][0] >  sentiment_counts_test['Count'][1]:
        
        if sentiment_counts_test['Count'][0] > sentiment_counts_test['Count'][2]: 
            st.markdown('<h3><span style="color:green;">Positively accepted the News</span></h3>', unsafe_allow_html=True)
    elif sentiment_counts_test['Count'][1] > sentiment_counts_test['Count'][2]:
        st.markdown('<h3><span style="color:red;">Negatively accepted the News</span></h3>', unsafe_allow_html=True) 
    else:
        st.markdown('<h3><span style="color:yellow;">Neutral(no effects)</span></h3>', unsafe_allow_html=True) 