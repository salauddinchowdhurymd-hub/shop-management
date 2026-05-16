import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt

# স্টাইলিং
st.markdown("""
    <style>
        body { background-color: #edf2f4; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        h1, h2, h3, h4 { color: #2b2d42; font-weight: 700; }
        .sidebar .sidebar-content { background-color: #d90429; }
        .css-1d391kg { border-radius: 15px; }
        .card {
            background: #ffffff; padding: 20px; border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        /* Buttons styling */
        .stButton>button { border-radius: 12px; background-color: #3b82f6; color: white; }
        /* DataTable styling */
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ইউজার ডেটা সেটআপ
if not os.path.exists('users.csv'):
    pd.DataFrame({'shop_name': ['দোকান১', 'দোকান২'], 'password': ['pass1', 'pass2']}).to_csv('users.csv', index=False)

users_df = pd.read_csv('users.csv')

# সেশন স্টেট
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['shop_name'] = ''
    st.session_state['logo_path'] = ''

# সাইন আপ ফাংশন
def signup():
    st.title("নতুন দোকান যোগ করুন")
    with st.form("signup_form"):
        new_shop = st.text_input("দোকানের নাম")
        new_pass = st.text_input("পাসওয়ার্ড", type='password')
        confirm_pass = st.text_input("পাসওয়ার্ড নিশ্চিত করুন", type='password')
        submit = st.form_submit_button("সাইন আপ")
        if submit:
            if new_shop == "" or new_pass == "":
                st.error("সব তথ্য দিন")
            elif new_pass != confirm_pass:
                st.error("পাসওয়ার্ড মিলছে না")
            elif new_shop in users_df['shop_name'].values:
                st.error("দোকানের নাম ইতিমধ্যে আছে")
            else:
                new_user = pd.DataFrame({'shop_name': [new_shop], 'password': [new_pass]})
                new_user.to_csv('users.csv', mode='a', header=False, index=False)
                st.success("নতুন দোকান যোগ হয়েছে, এখন লগইন করুন")
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
                        logo_path = f"{shop}_logo.png"
                        if os.path.exists(logo_path):
                            st.session_state['logo_path'] = logo_path
                    else:
                        st.error("ভুল পাসওয়ার্ড")
                else:
                    st.error("অজানা দোকান")
else:
    # লগআউট বাটন
    if st.button("লগআউট করুন"):
        st.session_state['logged_in'] = False
        st.session_state['shop_name'] = ''
        st.session_state['logo_path'] = ''
        st.experimental_rerun()

    shop_name = st.session_state['shop_name']
    st.markdown(f"<h2 style='text-align:center; color:#2b2d42;'>{shop_name} এ স্বাগতম</h2>", unsafe_allow_html=True)

    # লোগো দেখানো
    if st.session_state.get('logo_path'):
        st.image(st.session_state['logo_path'], width=150)

    # ডেটা লোড ও সংরক্ষণ
    def load_data(file_name, columns):
        if os.path.exists(file_name):
            return pd.read_csv(file_name)
        else:
            return pd.DataFrame(columns=columns)

    # ফাইলের নাম
    sales_file = f"{shop_name}_sales.csv"
    supplier_file = f"{shop_name}_supplier.csv"
    customer_file = f"{shop_name}_customer.csv"

    # ডেটা লোড
    sales_df = load_data(sales_file, ['তারিখ', 'বিবরণ', 'পেমেন্ট মেথড', 'ইন (টাকা)', 'আউট (টাকা)', 'প্রোডাক্ট'])
    supplier_df = load_data(supplier_file, ['তারিখ', 'মহাজনের নাম', 'মোট বিল', 'পরিশোধিত', 'পাওনা'])
    customer_df = load_data(customer_file, ['তারিখ', 'কাস্টমারের নাম', 'মালের দাম', 'জমা দিয়েছে', 'বাকি'])

    # লোগো আপলোড
    if 'logo_file' not in st.session_state:
        st.session_state['logo_file'] = None
    uploaded_logo = st.file_uploader("দোকানের লোগো আপলোড করুন", type=["png", "jpg", "jpeg"])
    if uploaded_logo:
        logo_path = f"{shop_name}_logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.read())
        st.session_state['logo_path'] = logo_path
        st.success("লোগো আপলোড হয়েছে!")

    # --- মেনু ---
    menu = [
        "📊 ড্যাশবোর্ড",
        "💰 দৈনন্দিন লেনদেন",
        "🤝 মহাজন/পার্টি হিসাব",
        "👤 কাস্টমার বাকি হিসাব",
        "🏦 ওয়ালেট ও ব্যাংক ব্যালেন্স",
        "📝 রিপোর্ট ডাউনলোড",
        "⚙️ ডেটা এডিট ও ডিলিট"
    ]
    choice = st.sidebar.selectbox("মেনু সিলেক্ট করুন", menu)

    # ড্যাশবোর্ড
    if choice == "📊 ড্যাশবোর্ড":
        st.subheader("সার্বিক অবস্থা")
        total_in = float(sales_df['ইন (টাকা)'].sum())
        total_out = float(sales_df['আউট (টাকা)'].sum())
        net_cash = total_in - total_out
        total_supplier_due = float(supplier_df['পাওনা'].sum())
        total_customer_due = float(customer_df['বাকি'].sum())

        total_sales = total_in
        total_expenses = total_out
        profit_loss = total_sales - total_expenses

        total_market_sales = 100000  # ধরুন
        market_share = (total_sales / total_market_sales) * 100

        # লাভ লোকসান
        if profit_loss >= 0:
            color = "#00b894"
            result_text = f"অভিনন্দন! লাভ হয়েছে: {profit_loss:.2f} টাকা"
        else:
            color = "#d63031"
            result_text = f"দুঃখের খবর, লোকসান: {abs(profit_loss):.2f} টাকা"

        col1, col2, col3 = st.columns(3)
        col1.metric("মোট ইনকাম", f"{total_in:.2f} টাকা")
        col2.metric("মোট আউট", f"{total_out:.2f} টাকা")
        col3.metric("বর্তমান ক্যাশ", f"{net_cash:.2f} টাকা")
        st.markdown(f"<h3 style='color:{color}; text-align:center;'>{result_text}</h3>", unsafe_allow_html=True)

        # মার্কেট শেয়ার ও গ্রাফ
        st.subheader("বাজারের অংশ")
        st.write(f"শেয়ার: {market_share:.2f}%")
        fig, ax = plt.subplots()
        ax.pie([market_share, 100 - market_share], labels=["আপনি", "অন্যরা"], autopct='%1.1f%%', colors=['#0984e3', '#dfe6e9'])
        st.pyplot(fig)

        # জনপ্রিয় পণ্য
        if 'প্রোডাক্ট' in sales_df.columns:
            top_products = sales_df['প্রোডাক্ট'].value_counts().head(5)
            st.subheader("শীর্ষ পণ্যসমূহ")
            st.bar_chart(top_products)

    # দৈনন্দিন লেনদেন
    elif choice == "💰 দৈনন্দিন লেনদেন":
        st.subheader("নতুন লেনদেন যোগ করুন")
        with st.form("cash_form"):
            date = st.date_input("তারিখ", datetime.date.today())
            desc = st.text_input("বিবরণ")
            method = st.selectbox("মাধ্যম", ["ক্যাশ", "ব্যাংক", "বিকাশ"])
            t_type = st.radio("টাইপ", ["টাকা আসছে (In)", "টাকা যাচ্ছে (Out)"])
            amount = st.number_input("পরিমাণ", min_value=0)
            if st.form_submit_button("সংরক্ষণ করুন"):
                v_in = amount if t_type == "টাকা আসছে (In)" else 0
                v_out = amount if t_type == "টাকা যাচ্ছে (Out)" else 0
                new_entry = {
                    'তারিখ': str(date),
                    'বিবরণ': desc,
                    'পেমেন্ট মেথড': method,
                    'ইন (টাকা)': v_in,
                    'আউট (টাকা)': v_out,
                    'প্রোডাক্ট': desc
                }
                sales_df = pd.concat([sales_df, pd.DataFrame([new_entry])], ignore_index=True)
                sales_df.to_csv(sales_file, index=False)
                st.success("লেনদেন সংরক্ষিত!")

        # গ্রাফ
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            monthly = sales_df.resample('M', on='তারিখ').sum()
            st.line_chart(monthly[['ইন (টাকা)', 'আউট (টাকা)']])
            st.download_button("এক্সেল ডাউনলোড", data=sales_df.to_csv(index=False).encode('utf-8'), file_name="sales_report.csv")

    # মহাজন/পার্টি হিসাব
    elif choice == "🤝 মহাজন/পার্টি হিসাব":
        st.subheader("মহাজন/পার্টি হিসাব দেখুন")
        if st.button("ডেটা দেখান"):
            if not supplier_df.empty:
                st.dataframe(supplier_df)
            else:
                st.info("কোন ডেটা পাওয়া যায়নি")
        with st.form("supplier_form"):
            date = st.date_input("তারিখ", datetime.date.today())
            name = st.text_input("মহাজনের নাম")
            total_bill = st.number_input("মোট বিল", min_value=0)
            paid = st.number_input("পরিশোধিত", min_value=0)
            due = total_bill - paid
            if st.form_submit_button("সংরক্ষণ করুন"):
                new_supplier = {
                    'তারিখ': str(date),
                    'মহাজনের নাম': name,
                    'মোট বিল': total_bill,
                    'পরিশোধিত': paid,
                    'পাওনা': due
                }
                supplier_df = pd.concat([supplier_df, pd.DataFrame([new_supplier])], ignore_index=True)
                supplier_df.to_csv(supplier_file, index=False)
                st.success("ডেটা সংরক্ষিত!")

    # কাস্টমার বাকি
    elif choice == "👤 কাস্টমার বাকি হিসাব":
        st.subheader("কাস্টমার বাকি দেখুন")
        if st.button("ডেটা দেখান"):
            if not customer_df.empty:
                st.dataframe(customer_df)
            else:
                st.info("কোন ডেটা পাওয়া যায়নি")
        with st.form("customer_form"):
            date = st.date_input("তারিখ", datetime.date.today())
            name = st.text_input("কাস্টমারের নাম")
            amount_paid = st.number_input("জমা দেওয়া টাকা", min_value=0)
            total_due = st.number_input("বাকি", min_value=0)
            if st.form_submit_button("সংরক্ষণ করুন"):
                new_customer = {
                    'তারিখ': str(date),
                    'কাস্টমারের নাম': name,
                    'মালের দাম': amount_paid,
                    'জমা দিয়েছে': amount_paid,
                    'বাকি': total_due
                }
                customer_df = pd.concat([customer_df, pd.DataFrame([new_customer])], ignore_index=True)
                customer_df.to_csv(customer_file, index=False)
                st.success("ডেটা সংরক্ষিত!")

    elif choice == "🏦 ওয়ালেট ও ব্যাংক ব্যালেন্স":
        st.subheader("ব্যাংক ও ওয়ালেট ব্যালেন্স")
        st.info("এখনও এই ফিচার আরও ডাইনামিক ও সুন্দর করে সাজানো হবে।")

    elif choice == "📝 রিপোর্ট ডাউনলোড":
        st.subheader("মাসিক রিপোর্ট ডাউনলোড করুন")
        months = pd.date_range('2023-01-01', periods=12, freq='MS').strftime("%B %Y")
        selected_month = st.selectbox("মাস নির্বাচন করুন", months)
        filtered = sales_df[pd.to_datetime(sales_df['তারিখ']).dt.strftime("%B %Y") == selected_month]
        if not filtered.empty:
            st.download_button("এক্সেল ডাউনলোড করুন", data=filtered.to_csv(index=False).encode('utf-8'), file_name=f"{selected_month}_report.csv")
        else:
            st.info("কোন ডেটা পাওয়া যায়নি এই মাসের জন্য।")

    elif choice == "⚙️ ডেটা এডিট ও ডিলিট":
        st.subheader("ডেটা এডিট ও ডিলিট")
        option = st.selectbox("অপশন", ["সেল এডিট", "রো ডিলিট"])
        if option == "সেল এডিট":
            edited_df = st.experimental_data_editor(sales_df)
            if st.button("সেভ করুন"):
                edited_df.to_csv(sales_file, index=False)
                st.success("ডেটা আপডেট হয়েছে")
        else:
            to_delete = st.multiselect("ডিলিট করতে চান এমন রো", sales_df.index)
            if st.button("ডিলিট করুন"):
                sales_df = sales_df.drop(to_delete)
                sales_df.to_csv(sales_file, index=False)
                st.success("ডেটা ডিলিট হয়েছে")
