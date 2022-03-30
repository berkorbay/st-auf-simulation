import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# from funs import get_prices
st.set_page_config(
    page_title="EPDK-EPIAS Azami Uzlaştırma Fiyatı Simülasyonu", layout="wide"
)


@st.cache
def get_data(file_name="epias_auf.xlsx"):
    return pd.read_excel(file_name, sheet_name="AUF")


def calculate_results(df, auf_d):
    excess_d = {}

    for key, value in auf_d.items():
        excess_d[key] = df.apply(
            lambda row: (row["PTF"] - value) * row[key], axis=1
        ).sum()

    return excess_d


st.session_state["auf"] = {}

st.title("EPDK-EPIAS Azami Uzlaştırma Fiyatı Simülasyonu")
st.markdown(
    "Şubat 2022 kaynağa göre üretim ve PTF verilerini kullanarak farklı Azami Uzlaştırma Fiyatı senaryolarında DBBT ve ÜDT değerlerini hesaplayın. Metodoloji ve kaynaklar sayfanın altında belirtilmiştir. Herhangi bir sorumluluk kabul edilmemektedir."
)


st.sidebar.header("Azami Uzlaştırma Fiyatı")
st.session_state["calc"] = st.sidebar.button("Hesapla")

for i in ["Doğal Gaz", "İthal Kömür"]:
    st.session_state["auf"][i] = st.sidebar.number_input(
        i, min_value=0, max_value=5000, value=2500, step=50
    )

for i in [
    "Linyit",
    "Asfaltit Kömür",
    "Taş Kömürü",
    "Barajlı",
    "Akarsu",
    "Rüzgar",
    "Jeotermal",
    "Biyokütle",
]:
    st.session_state["auf"][i] = st.sidebar.number_input(
        i, min_value=0, max_value=5000, value=1200, step=50
    )


if st.session_state["calc"]:
    x_d = calculate_results(df=st.session_state["rawdf"], auf_d=st.session_state["auf"])

    dbbt_val = sum([value if value > 0 else 0 for value in x_d.values()]) / 10 ** 6
    udt_val = sum([value if value < 0 else 0 for value in x_d.values()]) / 10 ** 6

    st.header("Özet Veriler")
    col1, col2, col3 = st.columns(3)
    col1.metric("DBBT", str(round(dbbt_val, 2)) + "M TL", None)
    col2.metric("ÜDT", str(round(abs(udt_val), 2)) + "M TL", None)
    col3.metric(
        "Destek Katsayısı", str(min(1.0, round(dbbt_val / abs(udt_val), 4))), None
    )
    st.markdown(
        "*Not: Destek Katsayısı 1 TL ÜDT'ye hak kazanan üreticinin ne kadar destekleneceğini belirtmektedir. Toplam DBBT, toplam ÜDT'den düşük olduğu durumlarda oransal destekleme yapılmaktadır.*"
    )

    st.header("Kaynağa göre AUF kaynaklı Farklar")
    st.markdown(
        """Sıfırdan küçükse Üretim Destekleme Tutarı (ÜDT), büyükse Destekleme Bedeli Borç Tutarı (DBBT) olarak kabul edilebilir."""
    )
    st.json(x_d)

st.header("Kaynak Veri")
with open("epias_auf.xlsx", "rb") as f:
    st.download_button("Veri dosyasını indir", f, file_name="epias_auf.xlsx")
st.session_state["own_data"] = st.checkbox(
    "Kendi verimi yüklemek istiyorum. (Notlara bakınız)"
)
if st.session_state["own_data"]:
    st_file = st.file_uploader("AUF Dosyası yükle", type="xlsx")
    if st_file is not None:
        st.session_state["rawdf"] = get_data(file_name=st_file)
    else:
        st.session_state["rawdf"] = get_data()
else:
    st.session_state["rawdf"] = get_data()


st.dataframe(st.session_state["rawdf"])

st.header("Notlar")
st.markdown(
    """
+ Hesaplama metodolojisi [Resmi Gazete\'de 18 Mart 'ta yayınlanan yönetmelik](https://www.resmigazete.gov.tr/eskiler/2022/03/20220318-16.pdf)ten alınmıştır. Sonraki mevzuatlarda metodoloji değişiklikleri varsa yansıtılmamıştır.
+ Şubat 2022'ye ait veriler [EPİAŞ Şeffaflık Platformu](https://seffaflik.epias.com.tr/)\'ndan alınmıştır.
+ İlgili metodolojiye ait olan hesaplamalar olabildiğince doğru bir şekilde yansıtılmaya çalışılmıştır ancak eksikler/yanlışlar olabilir.
+ Kendi veri setinizi kullanmak istiyorsanız kaynak veri seti dosyasını [indirip](https://github.com/berkorbay/st-auf-simulation/blob/main/epias_auf.xlsx?raw=true) değiştirerek sisteme yükleyebilirsiniz.
+ Üretim kaynakları olarak EPİAŞ Şeffaflık Platformu'ndaki UEVM başlıkları esas alınmıştır. Format tutarlılığı açısından isim değişikliği yapılmış olabilir.
+ Düşük üretim miktarına sahip bazı kaynaklar dahil edilmemiştir.
+ UEVM değerlerinden YEKDEM ve Lisanssız üretim verileri çıkarılmıştır. Güneş üretimi neredeyse tamamen YEKDEM ve Lisanssız üretim olduğu için hesaplamalara dahil edilmemektedir. Mevzuatta belirtilen diğer istisnalar (ör. yerli kömür, bazı ikili anlaşmalar) veri eksikliği sebebiyle düzenlenememiştir.
+ Veri ve koda ulaşmak için [Github](github.com/berkorbay/st-auf-simulation/) sayfasını ziyaret edebilirsiniz. 
+ Mevzuata göre desteklenmeye hak kazanan santraller eğer toplam DBBT, toplam ÜDT'ye eşit veya büyükse bütün desteği alabileceklerdir. Diğer durumda hak kazandıkları destek Destek Katsayısı ile çarpılarak bulunacaktır.
"""
)
