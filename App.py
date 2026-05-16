import streamlit as st
import pandas as pd
import os
import datetime

# স্টাইলিং
st.markdown("""
    <style>
        body { background-color: #f0f2f6; font-family: Arial, sans-serif; }
        h1, h2, h3 { color: #4CAF50; }
        .sidebar .sidebar-content { background-color: #4CAF50; }
        .css-1d391kg { border-radius: 10px; }
        .card { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .stButton>button { border-radius: 10px; background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

# ইউজার ডেটা
if not os.path.exists('users.csv'):
    pd.DataFrame({'shop_name': ['দোকান১'], 'password': ['1234']}).to_csv('users.csv', index=False)

users_df = pd.read_csv('users.csv')

# লগইন স্টেট
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['shop_name'] = ''

# সাইন আপ ফাংশন
def signup():
    st.title("নতুন দোকান যোগ করুন")
    with st.form("signup_form"):
        shop_name = st.text_input("দোকানের নাম")
        password = st.text_input("পাসওয়ার্ড", type='password')
        confirm_password = st.text_input("পাসওয়ার্ড নিশ্চিত করুন", type='password')
        submitted = st.form_submit_button("সাইন আপ")
        if submitted:
            if shop_name == "" or password == "":
                st.error("সব তথ্য দিন")
            elif password != confirm_password:
                st.error("পাসওয়ার্ড মিলছে না")
            elif shop_name in users_df['shop_name'].values:
                st.error("দোকানের নাম ইতিমধ্যে রয়েছে")
            else:
                new_user = pd.DataFrame({'shop_name': [shop_name], 'password': [password]})
                new_user.to_csv('users.csv', mode='a', header=False, index=False)
                st.success("নতুন দোকান যোগ হয়েছে। এখন লগইন করুন।")
                st.experimental_rerun()

# লগইন বা নতুন দোকান
if not st.session_state['logged_in']:
    st.sidebar.title("অ্যাকাউন্ট")
    option = st.sidebar.selectbox("অপশন", ["লগইন করুন", "নতুন দোকান যোগ করুন"])

    if option == "নতুন দোকান যোগ করুন":
        signup()
    else:
        st.title("লগইন করুন")
        with st.form("login_form"):
            shop_name = st.text_input("দোকানের নাম")
            password = st.text_input("পাসওয়ার্ড", type='password')
            login_button = st.form_submit_button("লগইন")
            if login_button:
                if shop_name in users_df['shop_name'].values:
                    correct_pwd = users_df[users_df['shop_name'] == shop_name]['password'].values[0]
                    if password == correct_pwd:
                        st.session_state['logged_in'] = True
                        st.session_state['shop_name'] = shop_name
                    else:
                        st.error("ভুল পাসওয়ার্ড")
                else:
                    st.error("অজানা দোকান")
else:
    # লগআউট
    if st.button("লগআউট"):
        st.session_state['logged_in'] = False
        st.session_state['shop_name'] = ''
        st.experimental_rerun()

    shop_name = st.session_state['shop_name']
    st.title(f"{shop_name} এর অ্যাপ্লিকেশন")
    # লোগো আপলোড
    logo_path = f"{shop_name}_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path)

    # ডেটা ফাইল
    sales_file = f"{shop_name}_sales.csv"

    # ডেটা লোড
    if os.path.exists(sales_file):
        sales_df = pd.read_csv(sales_file)
    else:
        sales_df = pd.DataFrame(columns=['তারিখ', 'বিবরণ', 'পেমেন্ট মেথড', 'ইন (টাকা)', 'আউট (টাকা)', 'প্রোডাক্ট'])

    # মেনু
    menu = ["ড্যাশবোর্ড", "দৈনিক লেনদেন", "রিপোর্ট ডাউনলোড", "ডেটা এডিট ও ডিলিট"]
    choice = st.sidebar.selectbox("মেনু", menu)

    if choice == "ড্যাশবোর্ড":
        st.header("সার্বিক অবস্থা")
        total_in = sales_df['ইন (টাকা)'].sum() if not sales_df.empty else 0
        total_out = sales_df['আউট (টাকা)'].sum() if not sales_df.empty else 0
        balance = total_in - total_out

        st.metric("মোট ইনকাম", f"{total_in:.2f} টাকা")
        st.metric("মোট আউট", f"{total_out:.2f} টাকা")
        st.metric("ব্যালেন্স", f"{balance:.2f} টাকা")

        # গ্রাফ
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            monthly = sales_df.resample('M', on='তারিখ').sum()
            st.line_chart(monthly[['ইন (টাকা)', 'আউট (টাকা)']])

    elif choice == "দৈনিক লেনদেন":
        st.header("নতুন লেনদেন যোগ করুন")
        with st.form("add_transaction"):
            date = st.date_input("তারিখ", datetime.date.today())
            description = st.text_input("বিবরণ")
            method = st.selectbox("মাধ্যম", ["ক্যাশ", "ব্যাংক", "বিকাশ"])
            type_ = st.radio("টাইপ", ["টাকা আসছে (In)", "টাকা যাচ্ছে (Out)"])
            amount = st.number_input("টাকার পরিমাণ", min_value=0)
            submitted = st.form_submit_button("সংরক্ষণ করুন")
            if submitted:
                new_entry = {
                    'তারিখ': str(date),
                    'বিবরণ': description,
                    'পেমেন্ট মেথড': method,
                    'ইন (টাকা)': amount if type_ == "টাকা আসছে (In)" else 0,
                    'আউট (টাকা)': amount if type_ == "টাকা যাচ্ছে (Out)" else 0,
                    'প্রোডাক্ট': description
                }
                sales_df = pd.concat([sales_df, pd.DataFrame([new_entry])], ignore_index=True)
                sales_df.to_csv(sales_file, index=False)
                st.success("লেনদেন সংরক্ষণ হয়েছে।")

        # গ্রাফ দেখানো
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            monthly = sales_df.resample('M', on='তারিখ').sum()
            st.line_chart(monthly[['ইন (টাকা)', 'আউট (টাকা)']])

    elif choice == "রিপোর্ট ডাউনলোড":
        st.header("মাসিক রিপোর্ট")
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            months = sales_df['তারিখ'].dt.strftime("%B %Y").unique()
            selected_month = st.selectbox("মাস নির্বাচন করুন", months)
            filtered = sales_df[sales_df['তারিখ'].dt.strftime("%B %Y") == selected_month]
            if not filtered.empty:
                st.download_button("এক্সেল ডাউনলোড", data=filtered.to_csv(index=False).encode('utf-8'), file_name=f"{selected_month}_report.csv")
        else:
            st.info("কোন ডেটা নেই।")

    elif choice == "ডেটা এডিট ও ডিলিট":
        st.header("ডেটা এডিট ও ডিলিট")
        option = st.selectbox("অপশন", ["সেল এডিট", "রো ডিলিট"])
        if option == "সেল এডিট":
            edited_df = st.experimental_data_editor(sales_df)
            if st.button("সেভ করুন"):
                edited_df.to_csv(sales_file, index=False)
                st.success("ডেটা আপডেট হয়েছে।")
        else:
            delete_indices = st.multiselect("ডিলিট করতে চান এমন রো", sales_df.index)
            if st.button("ডিলিট করুন"):
                sales_df = sales_df.drop(delete_indices)
                sales_df.to_csv(sales_file, index=False)
                st.success("ডেটা ডিলিট হয়েছে।")
