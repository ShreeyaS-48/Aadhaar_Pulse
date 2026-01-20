import os
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Loading Aadhaar dataset...")
def load_aadhaar_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")

    #Loading Aadhaar Enrolment, Demographic and Biometric Data
    df1 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_enrolment_0_500000.csv"))
    df2 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_enrolment_500000_1000000.csv"))
    df3 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_enrolment_1000000_1006029.csv"))
    df = pd.concat([df1, df2, df3])
    
    df_demo1 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_demographic_0_500000.csv"))
    df_demo2 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_demographic_500000_1000000.csv"))
    df_demo3 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_demographic_1000000_1500000.csv"))
    df_demo4 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_demographic_1500000_2000000.csv"))
    df_demo5 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_demographic_2000000_2071700.csv"))
    df_demo = pd.concat([df_demo1, df_demo2, df_demo3, df_demo4, df_demo5])
    
    df_bio1 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_biometric_0_500000.csv"))
    df_bio2 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_biometric_500000_1000000.csv"))
    df_bio3 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_biometric_1000000_1500000.csv"))
    df_bio4 = pd.read_csv(os.path.join(data_dir, "api_data_aadhar_biometric_1500000_1861108.csv"))
    df_bio = pd.concat([df_bio1, df_bio2, df_bio3, df_bio4])

    # Standardizing Date Format and Creating Additional Columns
    df['date'] = pd.to_datetime(df['date'], format = "%d-%m-%Y")
    df_demo['date'] = pd.to_datetime(df_demo['date'], format = "%d-%m-%Y")
    df_bio['date'] = pd.to_datetime(df_bio['date'], format = "%d-%m-%Y")
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df_demo['year'] = df_demo['date'].dt.year
    df_demo['month'] = df_demo['date'].dt.month
    df_bio['year'] = df_bio['date'].dt.year
    df_bio['month'] = df_bio['date'].dt.month

    df['total_enrolments'] = (
        df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    )
    df_demo['total_updates'] = (
        df_demo['demo_age_5_17'] + df_demo['demo_age_17_'] 
    )
    df_bio['total_updates'] = (
        df_bio['bio_age_5_17'] + df_bio['bio_age_17_'] 
    )
    
    state_map = {
        "Dadra And Nagar Haveli": "Dadra And Nagar Haveli And Daman And Diu",
        "Daman And Diu": "Dadra And Nagar Haveli And Daman And Diu",
        "West Bangal" : "West Bengal",
        "Westbengal" : "West Bengal",
        "West  Bengal" : "West Bengal",
        "Pondicherry" :"Puducherry",
        "The Dadra And Nagar Haveli And Daman And Diu" : "Dadra And Nagar Haveli And Daman And Diu",
        "Orissa" : "Odisha",
        "Balanagar" : "Telangana",
        "Chhatisgarh" : "Chhattisgarh",
        "Darbhanga" : "Bihar",
        "Jaipur" : "Rajasthan",
        "Madanapalle" : "Andhra Pradesh",
        "Puttenahalli" : "Karnataka",
        "Raja Annamalai Puram" : "Tamil Nadu",
        "Uttaranchal" : "Uttarakhand",
        "West Bengli" : "West Bengal",
        "Tamilnadu" : "Tamil Nadu",
        "Nagpur" : "Maharashtra"
    }
    district_map = {
        "Nicobars": "Nicobar",
        "Andamans": "North And Middle Andaman",
        "K.V.Rangareddy" : "K.V. Rangareddy",
        "Karimnagar" : "Karim Nagar",
        "Mahabubnagar" : "Mahabub Nagar",
        "Spsr Nellore" :"Sri Potti Sriramulu Nellore",
        "Aurangabad(Bh)":"Aurangabad",
        "Kaimur (Bhabua)" : "Kaimur",
        "Pashchim Champaran" :"West Champaran",
        "Purba Champaran" : "East Champaran",
        "Purbi Champaran" : "East Champaran",
        "Purnea" : "Purnia",
        "Samstipur": "Samastipur",
        "Sheikpura": "Sheikhpura",
        "Bhabua" :"Kaimur",
        "Monghyr" : "Munger",
        "Dakshin Bastar Dantewada" : "Dantewada",
        "Gaurella Pendra Marwahi" : "Gaurella-Pendra-Marwahi",
        "Janjgir Champa": "Janjgir-Champa",
        "Janjgir - Champa" : "Janjgir-Champa",
        "Kawardha" : "Kabirdham",
        "Kabeerdham" : "Kabirdham",
        "Mohla-Manpur-Ambagarh Chouki": "Mohla-Manpur-Ambagarh Chowki",
        "Uttar Bastar Kanker" :"Kanker",
        "Najafgarh" : "South West Delhi",
        "North East   *" : "North East Delhi",
        "North East" : "North East Delhi",
        "Bardez" : "North Goa",
        "Ahmadabad" : "Ahmedabad",
        "Banaskantha" :"Banas Kantha",
        "Dohad" : "Dahod",
        "Panchmahals" : "Panch Mahals",
        "Sabarkantha" : "Sabar Kantha",
        "Surendra Nagar" : "Surendranagar",
        "The Dangs" : "Dang",
        "Gurgaon" : "Gurugram",
        "Yamuna Nagar" : "Yamunanagar",
        "Mewat" : "Nuh",
        "Lahul And Spiti" : "Lahaul And Spiti",
        "Bandipore" : "Bandipora",
        "Bandipur" : "Bandipora",
        "Baramula" : "Baramulla",
        "East Singhbum": "East Singhbum",
        "Hazaribag" : "Hazaribagh",
        "Koderma" :"Kodarma",
        "Pakaur" : "Pakur",
        "Palamau" : "Palamu",
        "Sahebganj" : "Sahibganj",
        "Pashchimi Singhbhum" : "West Singhbhum",
        "Purbi Singhbhum" : "East Singhbum",
        "East Singhbhum" : "East Singhbum",
        "Bagalkot" : "Bagalkote",
        "Belgaum" : "Belgavi",
        "Bellary" : "Ballari",
        "Belgavi" : "Belgavi",
        "Bangalore Rural" :"Bengaluru Rural",
        "Bengaluru" : "Bengaluru Urban",
        "Bijapur" : "Vijayapura",
        "Bijapur(Kar)" :"Vijayapura",
        "Chamrajanagar" : "Chamarajanagar",
        "Chamrajnagar" :"Chamarajanagar",
        "Chickmagalur" : "Chikkaballapura",
        "Chikkaballapur" : "Chikkaballapura",
        "Chikmagalur" : "Chikkamagaluru",
        "Chickmagalur" : "Chikkamagaluru",
        "Davangere" : "Davanagere",
        "Gulbarga" : "Kalaburagi",
        "Hasan": "Hassan",
        "Mysore" : "Mysuru",
        "Tumkur": "Tumakuru",
        "Shimoga" : "Shivamogga",
        "Ramanagar" : "Bengaluru South",
        "Ramanagara" : "Bengaluru South",
        "Kasargod":"Kasaragod",
        "Ashok Nagar" : "Ashoknagar",
        "East Nimar" :"Khandwa",
        "Hoshangabad" : "Narmadapuram",
        "Narsinghpur" :  "Narsimhapur",
        "West Nimar" : "Khargone",
        "Ahmadnagar" : "Ahilyanagar",
        "Ahmed Nagar" : "Ahilyanagar",
        "Ahmednagar" : "Ahilyanagar",
        "Bid" : "Beed",
        "Buldana" : "Buldhana",
        "Chatrapati Sambhaji Nagar" : "Chatrapati Sambhajinagar",
        "Gondiya" :"Gondia",
        "Mumbai City": "Mumbai",
        "Mumbai( Sub Urban )" : "Mumbai Suburban",
        "Raigarh" : "Raigad",
        "Osmanabad" : "Dharashiv",
        "Raigarh(Mh)" : "Raigad",
        "Aurangabad" : "Chhatrapati Sambhajinagar",
        "Chatrapati Sambhajinagar" : "Chhatrapati Sambhajinagar",
        "Jaintia Hills" : "West Jaintia Hills",
        "Saiha" :"Siaha",
        "Mammit": "Mamit",
        "Anugal" : "Angul",
        "Anugul" : "Angul",
        "Baleshwar" : "Balasore",
        "Baleswar" : "Balasore",
        "Baudh" : "Boudh",
        "Jagatsinghpur" : "Jagatsinghapur",
        "Jajapur" : "Jajpur",
        "Kendujhar" : "Keonjhar",
        "Khorda" : "Khordha",
        "Nabarangapur" : "Nabarangpur",
        "Sonapur" : "Sonepur",
        "Subarnapur" : "Sonepur",
        "Sundergarh" :"Sundargarh",
        "Pondicherry" : "Puducherry",
        "Firozpur" : "Ferozepur",
        "Muktsar" : "Sri Muktsar Sahib",
        "Nawanshahr" : "Shaheed Bhagat Singh Nagar",
        "Sas Nagar (Mohali)" : "S.A.S Nagar",
        "S.A.S Nagar(Mohali)" : "S.A.S Nagar",
        "East Sikkim" : "Gangtok",
        "North Sikkim" : "Mangan",
        "South Sikkim" : "Namchi",
        "West Sikkim" : "Gyalshing",
        "Chittaurgarh" : "Chittorgarh",
        "Dhaulpur" : "Dholpur",
        "Jalor" : "Jalore",
        "Jhunjhunun" : "Jhunjhunu",
        "Kanchipuram" : "Kancheepuram",
        "Kanyakumari" : "Kanniyakumari",
        "Tirupattur" : "Tirupathur",
        "Tiruvallur" : "Thiruvallur", 
        "Tiruvarur" : "Thiruvarur",
        "Tuticorin" : "Thoothukkudi",
        "Villupuram" : "Vilupuram",
        "Vilupuram" : "Viluppuram",
        "Jangaon" : "Jangoan",
        "K.V. Rangareddy" : "Ranga Reddy",
        "Medchal-Malkajgiri" : "Medchal Malkajgiri",
        "Medchal?Malkajgiri" : "Medchal Malkajgiri",
        "Medchal−Malkajgiri" : "Medchal Malkajgiri",
        "Rangareddy" : "Ranga Reddy",
        "Warangal (Urban)" : "Warangal",
        "Warangal Rural" : "Warangal",
        "Warangal Urban" : "Warangal",
        "Allahabad" : "Prayagraj",
        "Bagpat" : "Baghpat",
        "Barabanki" : "Bara Banki",
        "Bulandshahar" : "Bulandshahr",
        "Faizabad" : "Ayodhya",
        "Jyotiba Phule Nagar" : "Amroha",
        "Kushi Nagar" : "Kushinagar",
        "Maharajganj" :"Mahrajganj",
        "Raebareli" : "Rae Bareli",
        "Sant Ravidas Nagar" : "Bhadohi",
        "Sant Ravidas Nagar Bhadohi" : "Bhadohi",
        "Shravasti" : "Shrawasti",
        "Siddharth Nagar" : "Siddharthnagar",
        "Garhwal" : "Pauri Garhwal",
        "Hardwar" : "Haridwar",
        "24 Paraganas North" : "North 24 Parganas",
        "24 Paraganas South" : "South 24 Parganas",
        "Dinajpur Dakshin" : "Dakshin Dinajpur",
        "Barddhaman" : "Paschim Bardhaman",
        "Bardhaman" : "Paschim Bardhaman",
        "Burdwan" : "Paschim Bardhaman",
        "Coochbehar" : "Cooch Behar",
        "Darjiling" : "Darjeeling",
        "Dinajpur Uttar" : "Uttar Dinajpur",
        "East Midnapore":"Purba Medinipur" ,
        "East Midnapur" :"Purba Medinipur",
        "Haora" : "Howrah",
        "Hawrah" : "Howrah",
        "Hooghiy" : "Hooghly",
        "Hugli" : "Hooghly",
        "Koch Bihar" : "Cooch Behar",
        "Maldah" : "Malda",
        "Medinipur" : "Purba Medinipur",
        "Medinipur West" : "Paschim Medinipur",
        "North 24 Paraganas" : "North 24 Parganas",
        "North Dinajpur" : "Uttar Dinajpur",
        "North Twenty Four Parganas" : "North 24 Parganas",
        "Puruliya" : "Purulia",
        "South 24 Pargana" : "South 24 Parganas",
        "South Twenty Four Parganas" : "South 24 Parganas",
        "South Dinajpur" : "Dakshin Dinajpur",
        "West Medinipur" : "Purba Medinipur",
        "West Midnapore" : "Purba Medinipur",
        "Karimganj" : "Sribhumi",
        "North Cachar Hills" : "Dima Hasao",
        "Sibsagar" : "Sivasagar",
        "Tamulpur District" : "Tamulpur",
        "Leh (Ladakh)" : "Leh"
    }

    df['state'] = (
        df['state']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
        .str.replace("&", "And")
    )
    df['district'] = (
        df['district']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
        .str.replace("&", "And")
        .str.replace(" *", "")
    )
    df['state'] = df['state'].replace(state_map)
    df = df[df['state'] != "100000"]
    df['district'] = df['district'].replace(district_map)

    

    df_demo['state'] = (
        df_demo['state']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
        .str.replace("&", "And")
    )
    df_demo['district'] = (
        df_demo['district']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
        .str.replace("&", "And")
        .str.replace(" *", "")
    )
    df_demo['state'] = df_demo['state'].replace(state_map)
    df_demo = df_demo[df_demo['state'] != "100000"]
    df_demo['district'] = df_demo['district'].replace(district_map)

    df_bio['state'] = (
        df_bio['state']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
        .str.replace("&", "And")
    )
    df_bio['district'] = (
        df_bio['district']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
        .str.replace("&", "And")
        .str.replace(" *", "")
    )
    df_bio['state'] = df_bio['state'].replace(state_map)
    df_bio = df_bio[df_bio['state'] != "100000"]
    df_bio['district'] = df_bio['district'].replace(district_map)
   

    df.loc[
        (df['state'] == 'Chandigarh') & (df['district'] == 'Rupnagar'),
        'state'
    ] = 'Punjab'
    df.loc[
        (df['state'] == 'Jammu And Kashmir') & (df['district'].isin(['Kargil', 'Leh'])),
        'state'
    ] = 'Ladakh'
    df.loc[
        (df['state'] == 'Meghalaya') & (df['district'] == 'Kamrup'),
        'state'
    ] = 'Assam'
    df.loc[
        (df['state'] == 'Sikkim') & (df['district'] == 'East'),
        'district'
    ] = 'Gangtok'
    df.loc[
        (df['state'] == 'Sikkim') & (df['district'] == 'West'),
        'district'
    ] = 'Gyalshing'
    df.loc[
        (df['state'] == 'Sikkim') & (df['district'] == 'North'),
        'district'
    ] = 'Mangan'
    df.loc[
        (df['state'] == 'Sikkim') & (df['district'] == 'South'),
        'district'
    ] = 'Namchi'
    
    
    

    

    df_demo.loc[
        (df_demo['state'] == 'Chandigarh') & (df_demo['district'] == 'Rupnagar'),
        'state'
    ] = 'Punjab'
    df_demo.loc[
        (df_demo['state'] == 'Jammu And Kashmir') & (df_demo['district'].isin(['Kargil', 'Leh'])),
        'state'
    ] = 'Ladakh'
    df_demo.loc[
        (df_demo['state'] == 'Meghalaya') & (df_demo['district'] == 'Kamrup'),
        'state'
    ] = 'Assam'
    df_demo.loc[
        (df_demo['state'] == 'Sikkim') & (df_demo['district'] == 'East'),
        'district'
    ] = 'Gangtok'
    df_demo.loc[
        (df_demo['state'] == 'Sikkim') & (df_demo['district'] == 'West'),
        'district'
    ] = 'Gyalshing'
    df_demo.loc[
        (df_demo['state'] == 'Sikkim') & (df_demo['district'] == 'North'),
        'district'
    ] = 'Mangan'
    df_demo.loc[
        (df_demo['state'] == 'Sikkim') & (df_demo['district'] == 'South'),
        'district'
    ] = 'Namchi'
    

    
    

    df_bio.loc[
        (df_bio['state'] == 'Chandigarh') & (df_bio['district'] == 'Rupnagar'),
        'state'
    ] = 'Punjab'
    df_bio.loc[
        (df_bio['state'] == 'Jammu And Kashmir') & (df_bio['district'].isin(['Kargil', 'Leh'])),
        'state'
    ] = 'Ladakh'
    df_bio.loc[
        (df_bio['state'] == 'Meghalaya') & (df_bio['district'] == 'Kamrup'),
        'state'
    ] = 'Assam'
    df_bio.loc[
        (df_bio['state'] == 'Sikkim') & (df_bio['district'] == 'East'),
        'district'
    ] = 'Gangtok'
    df_bio.loc[
        (df_bio['state'] == 'Sikkim') & (df_bio['district'] == 'West'),
        'district'
    ] = 'Gyalshing'
    df_bio.loc[
        (df_bio['state'] == 'Sikkim') & (df_bio['district'] == 'North'),
        'district'
    ] = 'Mangan'
    df_bio.loc[
        (df_bio['state'] == 'Sikkim') & (df_bio['district'] == 'South'),
        'district'
    ] = 'Namchi'
    return [df, df_demo, df_bio]

