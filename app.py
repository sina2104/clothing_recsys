﻿import streamlit as st
import cv2
import os 
import pandas as pd 
import random
import plotly.express as px
import yaml
import numpy as np

def read_data(input_dir):
    res_pair = pd.read_csv(input_dir + "submission.csv", dtype={'customer_id': str, 'prediction': str})
    res_resnet = pd.read_csv(input_dir + "resnet_submission.csv", dtype={'customer_id': str, 'prediction': str})
    res_lgbm = pd.read_csv(input_dir + "lgbm_submission.csv", dtype={'customer_id': str, 'prediction': str})
    df = pd.read_csv(input_dir + "transactions_train.csv", dtype={'article_id': str, 'sales_channel_id': str})
    df['t_dat'] = pd.to_datetime(df['t_dat'])
    df['n_weeks_ago'] = ((df['t_dat'].max() - df['t_dat']).dt.days // 7) + 1
    articles = pd.read_csv(input_dir + "articles.csv", dtype={'article_id': str})
    customers = pd.read_csv(input_dir + "customers.csv")
    return df, articles, customers, res_pair, res_resnet, res_lgbm

def get_sub_data(df, customers, articles, min_purchased_count):
    unique_customers = customers['customer_id'].unique()
    active_unique_customers = df.loc[df.groupby(['customer_id'])['article_id'].transform("count")>min_purchased_count, 'customer_id'].unique()
    unique_articles = articles['article_id'].unique()
    return unique_customers, active_unique_customers, unique_articles


def show_article_transactions(df, target_article_id):
    st.markdown("### Article Transactions")
    _df = df.loc[df['article_id']==target_article_id]
    st.dataframe(_df)
    fig = px.bar(
        _df.groupby(['n_weeks_ago', 'sales_channel_id'])['customer_id'].count().reset_index().rename(columns={'customer_id':'purchase count'}), 
        x='n_weeks_ago', y='purchase count', color='sales_channel_id', 
        range_x=[df['n_weeks_ago'].max(), df['n_weeks_ago'].min()],
        color_discrete_map={'1':'blue', '2':'red'}
        )
    fig.update_traces(width=1)
    st.plotly_chart(fig)


def visualize_article(df, articles, unique_articles, image_dir):
    target_article_id = select_target_article(unique_articles)
    st.markdown("### Article Information")
    col1, col2 = st.columns([1, 2])
    show_article_image(target_article_id, image_dir, col1)
    show_article_info(articles, target_article_id, col2)
    show_article_transactions(df, target_article_id)


def select_target_article(unique_articles):
    target_article_id = st.selectbox("Target Article ID", unique_articles)
    if (target_article_id != "") & (not target_article_id in unique_articles):
        st.error(f"{target_article_id} is not in the dataset. Please check the id is correct.")
    if st.button("Random Choice"):
        target_article_id = random.choice(unique_articles)
    return target_article_id


def show_article_info(articles, target_article_id, col):
    target_article_info = articles[articles['article_id']==target_article_id].T.astype(str)
    col.dataframe(target_article_info)


def show_article_image(target_article_id, image_dir, col):
    filename = str(image_dir + f'{target_article_id[:3]}/{target_article_id}.jpg')
    img = cv2.imread(filename)[:,:,::-1]
    col.image(img, use_column_width=True)


def visualize_customer(df, customers, unique_customers, active_unique_customers, num_sample, max_display_per_col, image_dir, res_pair, res_resnet, res_lgbm):
    target_customer_id = select_target_customer(unique_customers, active_unique_customers)
    show_customer_info(customers, target_customer_id)
    show_customer_transactions(df, target_customer_id)
    show_frequently_purchased_articles(df, target_customer_id, num_sample, max_display_per_col, image_dir)
    show_recently_purchased_articles(df, target_customer_id, num_sample, max_display_per_col, image_dir)
    show_prediction_pair(res_pair, target_customer_id, num_sample, max_display_per_col, image_dir)
    show_prediction_resnet(res_resnet, target_customer_id, num_sample, max_display_per_col, image_dir)
    show_prediction_lgbm(res_lgbm, target_customer_id, num_sample, max_display_per_col, image_dir)


def select_target_customer(unique_customers, active_unique_customers):
    target_customer_id = st.text_input(
        "Target Customer ID", 
        # value='e805d4c5a1f5b03312e4b98f29b8a61519ecac5eb01435013ad96413856c02dd',
        placeholder='Paste the target customer id'
        )
    # if not target_customer_id in unique_customers:
    #     st.error(f"{target_customer_id} is not in the dataset. Please check the id is correct.")
    if st.button("Random Choice"):
        target_customer_id = random.choice(active_unique_customers)
    return target_customer_id


def show_customer_info(customers, target_customer_id):
    target_customer_info = customers[customers['customer_id']==target_customer_id].T.astype(str)
    st.markdown("### Customer Information")
    st.dataframe(target_customer_info)


def show_customer_transactions(df, target_customer_id):
    st.markdown("### Customer Transactions")
    _df = df.loc[df['customer_id']==target_customer_id]
    st.dataframe(_df)
    fig = px.bar(
        _df.groupby(['n_weeks_ago', 'sales_channel_id'])['article_id'].count().reset_index().rename(columns={'article_id':'purchase count'}), 
        x='n_weeks_ago', y='purchase count', color='sales_channel_id', 
        range_x=[df['n_weeks_ago'].max(), df['n_weeks_ago'].min()],
        color_discrete_map={'1':'blue', '2':'red'}
        )
    fig.update_traces(width=1)
    st.plotly_chart(fig)


def show_frequently_purchased_articles(df, target_customer_id, num_sample, max_display_per_col, image_dir):
    st.markdown("### Frequently Purchased Articles")
    purchased_sample = df.loc[df['customer_id']==target_customer_id, 'article_id'].value_counts().head(num_sample)
    purchased_articles = purchased_sample.index
    purchased_count = purchased_sample.values

    col = st.columns(max_display_per_col)
    for i,article_id in enumerate(purchased_articles):
        j = i % max_display_per_col
        with col[j]:
            st.write(f"id: {article_id}")
            filename = str(image_dir + f'{article_id[:3]}/{article_id}.jpg')
            if os.path.exists(filename):
                img = cv2.imread(filename)[:,:,::-1]
                st.image(img, use_column_width=True)
                st.write(f"count: {purchased_count[i]}")
            else:
                st.error(f'Skip image because there is no file ({filename})')

def show_recently_purchased_articles(df, target_customer_id, num_sample, max_display_per_col, image_dir):
    st.markdown("### Recently Purchased Articles")
    recently_purchased_sample = df.loc[df['customer_id']==target_customer_id, ['t_dat', 'article_id']].drop_duplicates().sort_values('t_dat',ascending=False).head(num_sample)
    recently_purchased_articles = recently_purchased_sample['article_id'].to_numpy()
    print(recently_purchased_articles)
    recently_purchased_date = recently_purchased_sample['t_dat'].dt.strftime("%Y-%m-%d").to_numpy()
    col = st.columns(max_display_per_col)
    for i,article_id in enumerate(recently_purchased_articles):
        j = i % max_display_per_col
        with col[j]:
            print(article_id)
            st.write(f"id:{article_id}")
            filename = str(image_dir + f'{article_id[:3]}/{article_id}.jpg')
            if os.path.exists(filename):
                img = cv2.imread(filename)[:,:,::-1]
                st.image(img, use_column_width=True)
                st.write(f"date: {recently_purchased_date[i]}")
            else:
                st.error(f'Skip image because there is no file ({filename})')

def show_prediction_pair(res_pair, target_customer_id, num_sample, max_display_per_col, image_dir):
    st.markdown("### Pairwise prediction")
    pairwise_prediction_sample = res_pair.loc[res_pair['customer_id']==target_customer_id, ['prediction']].drop_duplicates().head(num_sample)
    pairwise_prediction_sample = pairwise_prediction_sample['prediction'].to_numpy()
    pairwise_prediction_sample = np.array(pairwise_prediction_sample[0].split())
    print(type(pairwise_prediction_sample))
    print(pairwise_prediction_sample)
    col = st.columns(max_display_per_col)
    for i,article_id in enumerate(pairwise_prediction_sample):
        j = i % max_display_per_col
        with col[j]:
            print(article_id)
            st.write(f"id:{article_id}")
            filename = str(image_dir + f'{article_id[:3]}/{article_id}.jpg')
            if os.path.exists(filename):
                img = cv2.imread(filename)[:,:,::-1]
                st.image(img, use_column_width=True)
            else:
                st.error(f'Skip image because there is no file ({filename})')

 
def show_prediction_resnet(res_resnet, target_customer_id, num_sample, max_display_per_col, image_dir):
    st.markdown("### Resnet prediction")
    resnet_prediction_sample = res_resnet.loc[res_resnet['customer_id']==target_customer_id, ['prediction']].drop_duplicates().head(num_sample)
    resnet_prediction_sample = resnet_prediction_sample['prediction'].to_numpy()
    resnet_prediction_sample = np.array(resnet_prediction_sample[0].split())
    print(type(resnet_prediction_sample))
    print(resnet_prediction_sample)
    col = st.columns(max_display_per_col)
    for i,article_id in enumerate(resnet_prediction_sample):
        j = i % max_display_per_col
        with col[j]:
            print(article_id)
            st.write(f"id:{article_id}")
            filename = str(image_dir + f'{article_id[:3]}/{article_id}.jpg')
            if os.path.exists(filename):
                img = cv2.imread(filename)[:,:,::-1]
                st.image(img, use_column_width=True)
            else:
                st.error(f'Skip image because there is no file ({filename})')

def show_prediction_lgbm(res_lgbm, target_customer_id, num_sample, max_display_per_col, image_dir):
    st.markdown("### LGBMranker prediction")
    resnet_prediction_sample = res_lgbm.loc[res_lgbm['customer_id']==target_customer_id, ['prediction']].drop_duplicates().head(num_sample)
    resnet_prediction_sample = resnet_prediction_sample['prediction'].to_numpy()
    resnet_prediction_sample = np.array(resnet_prediction_sample[0].split())
    print(type(resnet_prediction_sample))
    print(resnet_prediction_sample)
    col = st.columns(max_display_per_col)
    for i,article_id in enumerate(resnet_prediction_sample):
        j = i % max_display_per_col
        with col[j]:
            print(article_id)
            st.write(f"id:{article_id}")
            filename = str(image_dir + f'{article_id[:3]}/{article_id}.jpg')
            if os.path.exists(filename):
                img = cv2.imread(filename)[:,:,::-1]
                st.image(img, use_column_width=True)
            else:
                st.error(f'Skip image because there is no file ({filename})')

def main():
    # config
    with open('./config.yaml', 'r') as yml:
        config = yaml.safe_load(yml)

    data_dir = config["common"]['data_dir'] 
    image_dir = config["common"]['image_dir']
    min_purchased_count = config["customers"]['min_purchased_count']
    num_sample = config["customers"]['num_sample']
    max_display_per_col = config["customers"]['max_display_per_col']

    # read data(use cache to reduce loading time)
    df, articles, customers, res_pair, res_resnet, res_lgbm = read_data(data_dir)
    unique_customers, active_unique_customers, unique_articles = get_sub_data(df, customers, articles, min_purchased_count)

    # select type
    analysis_type = st.sidebar.radio("Select analysis type", ["Customers", "Articles"])

    # visualize
    if analysis_type == "Customers":
        visualize_customer(df, customers, unique_customers, active_unique_customers, num_sample, max_display_per_col, image_dir, res_pair, res_resnet, res_lgbm)
    elif analysis_type=="Articles":
        visualize_article(df, articles, unique_articles, image_dir)
    else:
        NotImplementedError


if __name__ == "__main__":
    main()