import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import io

# --- Definisi Fungsi make_prediction (PINDAHKAN KE ATAS) ---
def make_prediction(input_df):
    try:
        predictions = model.predict(input_df)
        probabilities = model.predict_proba(input_df) # Probabilitas untuk semua kelas
        return predictions, probabilities

    except Exception as e:
        st.error(f"Terjadi kesalahan saat melakukan prediksi: {e}")
        st.warning("Pastikan fitur-fitur yang Anda masukkan sesuai dengan yang diharapkan oleh model dan urutan kolomnya benar.")
        return None, None

# --- Bagian Konfigurasi (Sesuaikan dengan fitur model Anda) ---
# Daftar fitur yang diharapkan oleh model Anda.
# Ganti dengan nama fitur yang sebenarnya dari model Anda.
FEATURES = {
    "Numerical": [
        "Age_at_enrollment",
        "Unemployment_rate",
        "Inflation_rate",
        "GDP"
    ],
    "Float": [
        "Previous_qualification_grade",
        "Admission_grade"
    ],
    "Categorical": {
        "Scholarship_holder": {0: "Tidak", 1: "Ya"},
        "Gender": {0: "Perempuan", 1: "Laki-laki"},
        "Debtor": {0: "Tidak", 1: "Menunggak"},
        "Tuition_fees_up_to_date": {0: "Tidak", 1: "Ya"},
        "International": {0: "Tidak", 1: "Ya"},
        "Course": {
            33: "Biofuel Production Technologies",
            171: "Animation and Multimedia Design",
            8014: "Social Service (evening attendance)",
            9003: "Agronomy",
            9070: "Communication Design",
            9085: "Veterinary Nursing",
            9119: "Informatics Engineering",
            9130: "Equinculture",
            9147: "Management",
            9238: "Social Service",
            9254: "Tourism",
            9500: "Nursing",
            9556: "Oral Hygiene",
            9670: "Advertising and Marketing Management",
            9773: "Journalism and Communication",
            9853: "Basic Education",
            9991: "Management (evening attendance)"
        },
        "Previous_qualification": {
            1: "Secondary education",
            2: "Higher education - bachelor's degree",
            3: "Higher education - degree",
            4: "Higher education - master's",
            5: "Higher education - doctorate",
            6: "Frequency course",
            9: "12th year of schooling - not completed",
            10: "11th year of schooling - not completed",
            12: "Other - 11th year of schooling",
            14: "10th year of schooling",
            15: "10th year of schooling - not completed",
            19: "Basic education 3rd cycle (9th/10th/11th year) or equiv.",
            38: "Basic education 2nd cycle (6th/7th/8th year) or equiv.",
            39: "Technological specialization course",
            40: "Higher education - degree (1st cycle)",
            41: "Professional higher technical course",
            42: "Higher education - master's (2nd cycle)"
        },
        "Mothers_occupation": {
            1: "Student",
            2: "Representatives of the Legislative Power and Executive Bodies, Directors, Directors and Executive Managers",
            3: "Specialists in Intellectual and Scientific Activities",
            4: "Technicians and Professionals of Intermediate Level",
            5: "Administrative staff",
            6: "Skilled Workers in Agriculture, Animal Production, Forestry, Fisheries and Hunting",
            7: "Skilled workers in Industry, Construction and Craftsmen",
            8: "Installation and Machine Operators and Assembly Workers",
            9: "Unskilled Workers",
            10: "Armed Forces",
            90: "Other / Unknown"
        },
        "Application_mode": {
            1: "1st phase - general contingent",
            2: "Ordinance No. 612/93",
            5: "2nd phase - general contingent",
            7: "Holders of other higher courses",
            10: "Ordinance No. 854-B/99",
            15: "International student (Decree-Law No. 36/2014, of March 10)",
            16: "1st phase - special contingent",
            17: "2nd phase - special contingent",
            18: "3rd phase - general contingent",
            26: "Ordinance No. 533-A/99, item b2) (Different Plan)",
            27: "International student (Decree-Law No. 393-B/79)",
            42: "Ordinance No. 533-A/99, item b3 (Other Institution)",
            43: "Over 23 years old",
            44: "Transfer",
            51: "Change of course",
            53: "Technological specialization diploma holders",
            57: "Change of institution/course",
            69: "Applicants under 23 years old"
        },
        "Displaced": {0: "Tidak", 1: "Ya"}
    }
}

# --- Load model ---
try:
    model = joblib.load("model\model_selected_features.joblib") 
    st.success("Model berhasil dimuat!")
except FileNotFoundError:
    st.error("Error: File 'model.joblib' tidak ditemukan.")
    st.stop()
except Exception as e:
    st.error(f"Error saat memuat model: {e}")
    st.stop()

st.title("🎓 Prediksi Mahasiswa Dropout")
st.markdown("Isi informasi mahasiswa di bawah ini atau unggah file CSV untuk memprediksi kemungkinan dropout.")

# --- Opsi Input Data ---
input_option = st.radio("Pilih Metode Input Data:", ("Form Input", "Upload File CSV"))

# --- Form Input Pengguna ---
if input_option == "Form Input":
    st.subheader("📝 Masukkan Data Mahasiswa")
    user_input = {}

    # Input untuk fitur numerikal
    for feature in FEATURES["Numerical"]:
        user_input[feature] = st.number_input(f"{feature.replace('_', ' ')}",
                                              min_value=0.0,  # Sesuaikan
                                              max_value=100.0,  # Sesuaikan
                                              value=0.0,
                                              step=0.01,
                                              key=f"num_{feature}")

    # Input untuk fitur float
    for feature in FEATURES["Float"]:
        user_input[feature] = st.number_input(f"{feature.replace('_', ' ')}",
                                              min_value=0.0,
                                              max_value=200.0,
                                              value=0.0,
                                              step=0.01,
                                              key=f"float_{feature}")

    # Input untuk fitur kategorikal
    for feature, options_map in FEATURES["Categorical"].items():
        display_options = list(options_map.values())
        model_values = list(options_map.keys())

        selected_display_option = st.selectbox(f"{feature.replace('_', ' ')}",
                                               options=display_options,
                                               key=f"cat_{feature}")
        selected_model_value = model_values[display_options.index(selected_display_option)]
        user_input[feature] = selected_model_value

    # Tombol Prediksi (Form Input)
    if st.button("🔮 Prediksi (Form)"):
        all_features_order = FEATURES["Numerical"] + FEATURES["Float"] + list(FEATURES["Categorical"].keys())
        input_data = {col: [user_input[col]] for col in all_features_order}
        input_df = pd.DataFrame(input_data)
        st.subheader("📄 Data Input Anda (Form)")
        st.write(input_df)
        predictions, probabilities = make_prediction(input_df)  # Panggil fungsi prediksi

        if predictions is not None:
            if predictions[0] == 0:
                st.error(f"**Prediksi:** Mahasiswa ini **Cenderung Dropout**")
                st.write(f"**Probabilitas Dropout:** {probabilities[0][0]:.2%}")  # Corrected
            elif predictions[0] == 1:
                st.warning(f"**Prediksi:** Mahasiswa ini **Cenderung Enrolled**")
                st.write(f"**Probabilitas Enrolled:** {probabilities[0][1]:.2%}")  # Corrected
            else:
                st.success(f"**Prediksi:** Mahasiswa ini **Cenderung Graduate**")
                st.write(f"**Probabilitas Graduate:** {probabilities[0][2]:.2%}")  # Corrected

# --- Upload File CSV ---
elif input_option == "Upload File CSV":
    uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])
    delimiter = st.radio("Pilih Delimiter:", (",", ";"))

    if uploaded_file is not None:
        try:
            # Baca file CSV menggunakan pandas
            csv_data = uploaded_file.read()
            input_df = pd.read_csv(io.StringIO(csv_data.decode("utf-8")), delimiter=delimiter)

            # Validasi kolom
            all_features_order = FEATURES["Numerical"] + FEATURES["Float"] + list(FEATURES["Categorical"].keys())
            if not set(all_features_order).issubset(input_df.columns):
                missing_cols = set(all_features_order) - set(input_df.columns)
                st.error(f"File CSV tidak memiliki kolom yang diperlukan: {missing_cols}")
            else:
                st.subheader("📊 Data dari File CSV")
                st.write(input_df)

                # Tambahkan tombol prediksi untuk upload file
                if st.button("🔮 Prediksi (File)"):
                    # Pilih hanya kolom yang dibutuhkan model
                    input_df = input_df[all_features_order]

                    # Lakukan prediksi untuk setiap baris
                    predictions, probabilities = make_prediction(input_df)

                    if predictions is not None:
                        # Tambahkan kolom prediksi dan probabilitas ke DataFrame
                        input_df["Prediksi Dropout"] = predictions
                        # Buat fungsi untuk mendapatkan probabilitas yang sesuai
                        def get_probability(row):
                            if row["Prediksi Dropout"] == 0:
                                return probabilities[row.name][0]
                            elif row["Prediksi Dropout"] == 1:
                                return probabilities[row.name][1]
                            else:
                                return probabilities[row.name][2]

                        input_df["Probabilitas"] = input_df.apply(get_probability, axis=1)

                        # Map nilai prediksi ke label yang sesuai
                        status_mapping = {0: "Dropout", 1: "Enrolled", 2: "Graduate"}
                        input_df["Prediksi"] = input_df["Prediksi Dropout"].map(status_mapping)
                        # Tampilkan DataFrame dengan hasil prediksi
                        st.subheader("📝 Hasil Prediksi per Mahasiswa")
                        st.write(input_df[["Prediksi", "Probabilitas"]])  # Tampilkan hanya kolom Prediksi dan Probabilitas

                        # Hitung Persentase Dropout
                        dropout_count = (input_df["Prediksi Dropout"] == 0).sum()
                        total_count = len(input_df)
                        dropout_percentage = (dropout_count / total_count) * 100

                        st.subheader("📊 Analisis Keseluruhan")
                        st.write(f"Persentase Mahasiswa yang Diprediksi Dropout: {dropout_percentage:.2f}%")

                        # Visualisasi Pie Chart
                        labels = 'Dropout', 'Not Dropout'
                        sizes = [dropout_count, total_count - dropout_count]
                        fig1, ax1 = plt.subplots()
                        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                shadow=True, startangle=90)
                        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                        st.pyplot(fig1)


        except pd.errors.EmptyDataError:
            st.error("File CSV kosong.")
        except pd.errors.ParserError:
            st.error("Error memparsing file CSV. Pastikan formatnya benar.")
        except Exception as e:
            st.error(f"Error saat memproses file CSV: {e}")

