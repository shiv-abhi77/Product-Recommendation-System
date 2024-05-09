import itertools
import streamlit as st
import numpy as np
import pandas as pd
import pickle as pkl
from urllib.request import urlopen


@st.cache_resource
def load():
    models = pkl.load(open('Model.pkl', 'rb'))
    return models


Sim_Models = load()


# Info_Text = st.text('Please Select a Product to Buy')

@st.cache_resource
def Load_Data_User():
    return pd.read_csv(r'FlipDatasetProcessed.csv', index_col=0), pd.read_csv(r'UserData.csv', index_col=0)


data, user_df = Load_Data_User()

st.title('Product Recommendation System')


def get_recommendation(model, usr_index):
    # user_df = pd.read_csv("UserData.csv", index_col=0)
    # prod_df = pd.read_csv("FlipDatasetProcessed.csv", index_col=0)
    sim_users = [index for index, _ in
                 sorted(list(enumerate(model[0][usr_index])), reverse=True, key=lambda x: x[1])[:5]]
    items = []
    gender = user_df.iloc[usr_index]['Gender']

    def is_ok(idx, gender):
        if not data.iloc[idx].show:
            return False
        desc = data['desc'][idx]
        male = False
        female = False
        for word in desc.split(' '):
            if word in ["woman", "women", "womens", "women's", "girl", "girls", "lady", "ladies"]:
                female = True
            if word in ["man", "men", "mens" "boy", "men's", "boys", "guy", "guys"]:
                male = True
        return male or not female if gender == 'Male' else female or not male

    for sim_usr_ind in sim_users:
        prod_ind = user_df.iloc[sim_usr_ind]['item_index']
        lst = sorted(list(enumerate(model[1][prod_ind])), reverse=True, key=lambda x: x[1])
        filtered = filter(lambda x: is_ok(x[0], gender), lst)
        top10 = itertools.islice(filtered, 5)

        for ind, _ in top10:
            items.append(ind)
    return items, sim_users


# usr_ind = 0
# print(f"User: {user_df.iloc[usr_ind]}")
# print()
# rec = get_recommendation(Sim_Models, usr_ind)
# for idx in rec:
#     print(data.iloc[idx]['product_name'])

if 'newProducts' not in st.session_state:
    st.session_state.newProducts = []
if 'flag' not in st.session_state:
    st.session_state.flag = False
if 'sim_User' not in st.session_state:
    st.session_state.sim_User = []


def load_prod_name():
    name = data[data.show]['product_name']
    return name


def load_user_name():
    name = user_df['Name']
    return name


products = load_prod_name()
users = load_user_name()


# @st.cache_data
def predict_prod(ind):
    lst = sorted(list(enumerate(Sim_Models[1][ind])), reverse=True, key=lambda x: x[1])
    filtered = filter(lambda x: data.iloc[x[0]].show, lst)
    top10 = itertools.islice(filtered, 10)
    return top10


# def resize_image(image, size):
#     resized_image = image.resize(size)
#     return resized_image
# def set():
#     st.session_state.flag = False
selected_User = st.selectbox("Select Your User", range(len(users)), format_func=lambda x: users[x])

newProducts = []
if st.button("Recommend On Users"):
    predicts, sim_users = get_recommendation(Sim_Models, selected_User)
    for i in predicts:
        newProducts.append((products.iloc[i], i))
    st.session_state.newProducts = newProducts
    st.session_state.sim_User = sim_users
    # st.session_state.flag = True

st.write()
st.divider()
st.write()

selected = st.selectbox("Select Your Product", range(len(st.session_state.newProducts)),
                        format_func=lambda x: st.session_state.newProducts[x][0])
if st.button("Recommend"):
    predicts = predict_prod(st.session_state.newProducts[selected][1])
    for i in predicts:
        with st.expander(data.iloc[i[0]]['product_name']):
            st.text(f"Category:{data.iloc[i[0]]['product_category_tree']}")
            st.write()
            img = data.iloc[i[0]]['image']
            imgst = img.split('"')


            # st.write(imgst[1])
            # size = (640, 853)
            # resized_image = resize_image(imgst[1], size)
            def checkURL(url):
                try:
                    urlopen(url)
                    return True
                except:
                    return False


            img_ind = 1
            while img_ind < len(imgst) and not checkURL(img_ind):
                img_ind += 1
            if img_ind == len(imgst):
                img_ind = 1
            st.image(imgst[img_ind], width=150)
            st.write(f"Price: {data.iloc[i[0]]['discounted_price']}")

    # st.write(f"Product Name: {data.iloc[i[0]]['product_name']}       Category: {data.iloc[i[0]][
    # 'product_category_tree']}     Price:{data.iloc[i[0]]['discounted_price']}")
st.write()
st.divider()
st.write()
with st.sidebar:
    for ind in st.session_state.sim_User:
        # for ind in sim_users:
        with st.expander(user_df.iloc[ind]['Name']):
            # st.text(f"Category:{user_df.iloc[ind]['Name']}")
            st.write(f"Gender: {user_df.iloc[ind]['Gender']}")
            st.write(f"Age: {user_df.iloc[ind]['Age']}")
            st.write(f"Products: {user_df.iloc[ind]['prod_name']}")
            st.write(f"Products Cat: {user_df.iloc[ind]['category']}")
            st.write(f"Avg_Price: {user_df.iloc[ind]['avg_price']}")
