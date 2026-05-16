import streamlit as st
import pandas as pd
import datetime
import os

# CSS স্টাইলিং
st.markdown("""
    <style>
        /* পুরো অ্যাপের ব্যাকগ্রাউন্ড কালার */
        body {
            background-color: #f0f2f6;
            font-family: Arial, sans-serif;
        }
        /* হেডার ও সাবহেডার স্টাইল */
        h1, h2, h3 {
            color: #4CAF50;
        }
        /* বাটন ও ইনপুটের স্টাইল */
        .css-1d391kg {
            border-radius: 10px;
        }
        /* কার্ড বা কন্টেইনার */
        .card {
            background: #fff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ইউজার ডেটা থাকলে লোড করুন, না থাকলে তৈরি করুন
if not os.path.exists('users.csv'):
    pd.DataFrame({
        'shop_name': ['দোকান১', 'দোকান২'],
        'password': ['pass1', 'pass2']
    }).to_csv('users.csv', index=False)

users_df = pd.read_csv('users.csv')

# লগইন স্টেট সেটআপ
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['shop_name'] = ''
    st.session_state['logo_path'] = ''

# সাইন আপ করার ফাংশন
def signup():
    st.title("নতুন দোকান যোগ করুন")
    with st.form("signup_form"):
        new_shop = st.text_input("দোকানের নাম")
        new_pass = st.text_input("পাসওয়ার্ড", type='password')
        confirm_pass = st.text_input("পাসওয়ার্ড নিশ্চিত করুন", type='password')
        submit = st.form_submit_button("সাইন আপ")
        if submit:
            if new_shop == "" or new_pass == "":
                st.error("দয়া করে সকল তথ্য দিন")
            elif new_pass != confirm_pass:
                st.error("পাসওয়ার্ড মিলছে না")
            elif new_shop in users_df['shop_name'].values:
                st.error("দোকানের নাম ইতিমধ্যে exists")
            else:
                new_user = pd.DataFrame({'shop_name': [new_shop], 'password': [new_pass]})
                new_user.to_csv('users.csv', mode='a', header=False, index=False)
                st.success("নতুন দোকান সফলভাবে যোগ হয়েছে, এখন লগইন করুন")
                st.experimental_rerun()

# লগইন বা সাইনআপ অপশন
if not st.session_state['logged_in']:
    st.sidebar.title("অ্যাকাউন্ট")
    login_option = st.sidebar.selectbox("অ্যাকাউন্ট অপশন", ["লগইন করুন", "নতুন দোকান যোগ করুন"])
    if login_option == "নতুন দোকান যোগ করুন":
        signup()
    else:
        st.title("লগইন করুন")
        with st.form("login_form"):
            shop = st.text_input("দোকানের নাম")
            pwd = st.text_input("পাসওয়ার্ড", type='password')
            login_button = st.form_submit_button("লগইন")
            if login_button:
                if shop in users_df['shop_name'].values:
                    correct_pwd = users_df[users_df['shop_name'] == shop]['password'].values[0]
                    if pwd == correct_pwd:
                        st.session_state['logged_in'] = True
                        st.session_state['shop_name'] = shop
                        # যদি লোগো আপলোড করে থাকে, সেটি লোড করো
                        logo_path = f"{shop}_logo.png"
                        if os.path.exists(logo_path):
                            st.session_state['logo_path'] = logo_path
                    else:
                        st.error("ভুল পাসওয়ার্ড")
                else:
                    st.error("অজানা দোকানের নাম")
else:
    # লগআউট বোতাম
    if st.button("লগআউট"):
        st.session_state['logged_in'] = False
        st.session_state['shop_name'] = ''
        st.session_state['logo_path'] = ''
        st.experimental_rerun()

    shop_name = st.session_state['shop_name']
    st.markdown(f"<h2 style='text-align:center;'>স্বাগতম, {shop_name}</h2>", unsafe_allow_html=True)

    # লোগো দেখাও
    if st.session_state.get('logo_path'):
        st.image(st.session_state['logo_path'], width=150)

    # ডেটা লোড করার ফাংশন
    def load_shop_data(file_name, columns):
        if os.path.exists(file_name):
            return pd.read_csv(file_name)
        else:
            return pd.DataFrame(columns=columns)

    # ডেটা ফাইলের নাম নির্ধারণ
    sales_file = f"{shop_name}_sales.csv"
    supplier_file = f"{shop_name}_supplier.csv"
    customer_file = f"{shop_name}_customer.csv"

    # ডেটা লোড
    sales_df = load_shop_data(sales_file, ['তারিখ', 'বিবরণ', 'পেমেন্ট মেথড', 'ইন (টাকা)', 'আউট (টাকা)', 'প্রোডাক্ট'])
    supplier_df = load_shop_data(supplier_file, ['তারিখ', 'মহাজনের নাম', 'মোট বিল', 'পরিশোধিত', 'পাওনা'])
    customer_df = load_shop_data(customer_file, ['তারিখ', 'কাস্টমারের নাম', 'মালের দাম', 'জমা দিয়েছে', 'বাকি'])
    # দোকানের লোগো আপলোড
    if 'logo_file' not in st.session_state:
        st.session_state['logo_file'] = None
    uploaded_logo = st.file_uploader("দোকানের লোগো আপলোড করুন", type=["png", "jpg", "jpeg"])
    if uploaded_logo:
        logo_path = f"{shop_name}_logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.read())
        st.session_state['logo_path'] = logo_path
        st.success("লোগো আপলোড হয়েছে!")

    # --- সাইডবার মেনু ---
    menu = [
        "📊 ড্যাশবোর্ড",
        "💰 দৈনন্দিন লেনদেন",
        "🤝 মহাজন/পার্টি হিসাব",
        "👤 কাস্টমার বাকি হিসাব",
        "🏦 ওয়ালেট ও ব্যাংক ব্যালেন্স"
    ]
    choice = st.sidebar.selectbox("মেনু সিলেক্ট করুন", menu)

    # --- ড্যাশবোর্ড ---
    if choice == "📊 ড্যাশবোর্ড":
        st.subheader("দোকানের সার্বিক অবস্থা")
        total_cash_in = sales_df['ইন (টাকা)'].sum()
        total_cash_out = sales_df['আউট (টাকা)'].sum()
        net_cash = total_cash_in - total_cash_out
        total_supplier_due = supplier_df['পাওনা'].sum()
        total_customer_due = customer_df['বাকি'].sum()

        # লাভ-লোকসান হিসাব
        total_sales = sales_df['ইন (টাকা)'].sum()
        total_expenses = sales_df['আউট (টাকা)'].sum()
        profit_loss = total_sales - total_expenses
        # মার্কেট শেয়ার হিসাব
        total_market_sales = 100000  # ধরুন মোট মার্কেটের বিক্রি
        user_sales = total_sales
        market_share = (user_sales / total_market_sales) * 100

        # লাভ বা লোকসান দেখাও
        if profit_loss >= 0:
            result_text = f"আরে বাহ! লাভ হয়েছে: {profit_loss} টাকা"
        else:
            result_text = f"দুঃখের খবর, লোকসান: {abs(profit_loss)} টাকা"

        col1, col2, col3 = st.columns(3)
        col1.metric("মোট ক্যাশ ইন", f"{total_cash_in} টাকা")
        col2.metric("মোট ক্যাশ আউট", f"{total_cash_out} টাকা")
        col3.metric("বর্তমানে হাতে আছে", f"{net_cash} টাকা")

        st.markdown(f"<h3 style='text-align:center;'>{result_text}</h3>", unsafe_allow_html=True)

        # মার্কেট শেয়ার দেখানো
        st.write(f"সাধারণ মার্কেট শেয়ার: {market_share:.2f}%")
        st.progress(min(market_share/100, 1))

        # পপুলার প্রোডাক্ট দেখানো
        if 'প্রোডাক্ট' in sales_df.columns:
            top_products = sales_df['প্রোডাক্ট'].value_counts().head(5)
            st.subheader("সর্বাধিক বিক্রীত পণ্যসমূহ")
            st.bar_chart(top_products)

    # --- ড্যাশবোর্ডের অন্যান্য অপশন ---
    elif choice == "💰 দৈনন্দিন লেনদেন":
        st.subheader("নতুন ক্যাশ ইন/আউট এন্ট্রি")
        with st.form("cash_form"):
            date = st.date_input("তারিখ", datetime.date.today())
            desc = st.text_input("বিবরণ (উদা: ৫টি শার্ট বিক্রি)")
            method = st.selectbox("মাধ্যম", ["ক্যাশ", "ব্যাংক", "বিকাশ"])
            t_type = st.radio("ধরণ", ["টাকা আসছে (In)", "টাকা গেছে (Out)"])
            amount = st.number_input("টাকার পরিমাণ", min_value=0)
            if st.form_submit_button("লেনদেন সেভ করুন"):
                v_in = amount if t_type == "টাকা আসছে (In)" else 0
                v_out = amount if t_type == "টাকা গেছে (Out)" else 0
                new_row = {
                    'তারিখ': date,
                    'বিবরণ': desc,
                    'পেমেন্ট মেথড': method,
                    'ইন (টাকা)': v_in,
                    'আউট (টাকা)': v_out,
                    'প্রোডাক্ট': desc  # দরকার হলে যুক্ত করো
                }
                sales_df = pd.concat([sales_df, pd.DataFrame([new_row])], ignore_index=True)
                sales_df.to_csv(sales_file, index=False)
                st.success("হিসাব আপডেট হয়েছে!")

    # আরও অপশনগুলো ইমপ্লিমেন্ট করে দিতে পারো...
