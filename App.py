import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

# স্টাইলিং
st.markdown("""
    <style>
        body { background-color: #f0f2f6; font-family: Arial, sans-serif; }
        h1, h2, h3 { color: #4CAF50; }
        .sidebar .sidebar-content { background-color: #4CAF50; }
        .css-1d391kg { border-radius: 10px; }
        .card { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .stButton>button { border-radius: 10px; background-color: #4CAF50; color: white; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ইউজার ডেটা সেটআপ
if not os.path.exists('users.csv'):
    pd.DataFrame({'shop_name': ['দোকান১'], 'password': ['1234']}).to_csv('users.csv', index=False)

users_df = pd.read_csv('users.csv')

# সেশন স্টেট
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
    supplier_file = f"{shop_name}_supplier.csv"
    customer_file = f"{shop_name}_customer.csv"

    # ডেটা লোড
    if os.path.exists(sales_file):
        sales_df = pd.read_csv(sales_file)
    else:
        sales_df = pd.DataFrame(columns=['তারিখ', 'বিবরণ', 'পেমেন্ট মেথড', 'ইন (টাকা)', 'আউট (টাকা)', 'প্রোডাক্ট'])

    if os.path.exists(supplier_file):
        supplier_df = pd.read_csv(supplier_file)
    else:
        supplier_df = pd.DataFrame(columns=['তারিখ', 'মহাজনের নাম', 'মোট বিল', 'পরিশোধিত', 'পাওনা'])

    if os.path.exists(customer_file):
        customer_df = pd.read_csv(customer_file)
    else:
        customer_df = pd.DataFrame(columns=['তারিখ', 'কাস্টমারের নাম', 'মালের দাম', 'জমা দিয়েছে', 'বাকি'])

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
        total_in = sales_df['ইন (টাকা)'].sum() if not sales_df.empty else 0
        total_out = sales_df['আউট (টাকা)'].sum() if not sales_df.empty else 0
        balance = total_in - total_out

        st.metric("মোট ইনকাম", f"{total_in:.2f} টাকা")
        st.metric("মোট আউট", f"{total_out:.2f} টাকা")
        st.metric("বর্তমান ব্যালেন্স", f"{balance:.2f} টাকা")

        # গ্রাফ
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            monthly = sales_df.resample('M', on='তারিখ').sum()
            st.line_chart(monthly[['ইন (টাকা)', 'আউট (টাকা)']])

        # বাজারের শেয়ার
        total_market_sales = 100000  # উদাহরণ
        market_share = (total_in / total_market_sales) * 100 if total_market_sales else 0
        st.write(f"বাজারের অংশ: {market_share:.2f}%")
        fig, ax = plt.subplots()
        ax.pie([market_share, 100 - market_share], labels=["আপনি", "অন্যরা"], autopct='%1.1f%%', colors=['#0984e3', '#dfe6e9'])
        st.pyplot(fig)

        # শীর্ষ পণ্য
        if 'প্রোডাক্ট' in sales_df.columns:
            top_products = sales_df['প্রোডাক্ট'].value_counts().head(5)
            st.subheader("শীর্ষ পণ্যসমূহ")
            st.bar_chart(top_products)

    # দৈনন্দিন লেনদেন
    elif choice == "💰 দৈনন্দিন লেনদেন":
        st.subheader("নতুন লেনদেন যোগ করুন")
        with st.form("add_transaction"):
            date = st.date_input("তারিখ", datetime.date.today())
            description = st.text_input("বিবরণ")
            method = st.selectbox("মাধ্যম", ["ক্যাশ", "ব্যাংক", "বিকাশ"])
            t_type = st.radio("টাইপ", ["টাকা আসছে (In)", "টাকা যাচ্ছে (Out)"])
            amount = st.number_input("পরিমাণ", min_value=0)
            submitted = st.form_submit_button("সংরক্ষণ করুন")
            if submitted:
                new_entry = {
                    'তারিখ': str(date),
                    'বিবরণ': description,
                    'পেমেন্ট মেথড': method,
                    'ইন (টাকা)': amount if t_type == "টাকা আসছে (In)" else 0,
                    'আউট (টাকা)': amount if t_type == "টাকা যাচ্ছে (Out)" else 0,
                    'প্রোডাক্ট': description
                }
                sales_df = pd.concat([sales_df, pd.DataFrame([new_entry])], ignore_index=True)
                sales_df.to_csv(sales_file, index=False)
                st.success("লেনদেন সংরক্ষিত।")

        # গ্রাফ
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            monthly = sales_df.resample('M', on='তারিখ').sum()
            st.line_chart(monthly[['ইন (টাকা)', 'আউট (টাকা)']])

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
                st.success("ডেটা সংরক্ষণ হয়েছে।")

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
                st.success("ডেটা সংরক্ষিত।")

    elif choice == "🏦 ওয়ালেট ও ব্যাংক ব্যালেন্স":
        st.subheader("ব্যাংক ও ওয়ালেট ব্যালেন্স")
        st.info("এই ফিচারটি আরও ডাইনামিক ও সুন্দর করে সাজানো হবে।")

    elif choice == "📝 রিপোর্ট ডাউনলোড":
        st.subheader("মাসিক রিপোর্ট ডাউনলোড করুন")
        if not sales_df.empty:
            sales_df['তারিখ'] = pd.to_datetime(sales_df['তারিখ'])
            months = sales_df['তারিখ'].dt.strftime("%B %Y").unique()
            selected_month = st.selectbox("মাস নির্বাচন করুন", months)
            filtered = sales_df[sales_df['তারিখ'].dt.strftime("%B %Y") == selected_month]
            if not filtered.empty:
                st.download_button("এক্সেল ডাউনলোড করুন", data=filtered.to_csv(index=False).encode('utf-8'), file_name=f"{selected_month}_report.csv")
        else:
            st.info("কোন ডেটা নেই।")

    elif choice == "⚙️ ডেটা এডিট ও ডিলিট":
        st.subheader("ডেটা এডিট ও ডিলিট")
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
