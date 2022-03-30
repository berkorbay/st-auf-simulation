import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# from funs import get_prices
st.set_page_config(
    page_title="EPDK-EPİAŞ Azami Uzlaştırma Fiyatı Simülasyonu",
    page_icon=":bolt:",
    layout="wide",
)

st.session_state["min_price"] = 0
st.session_state["max_price"] = 2500


@st.cache
def get_data(file_name="epias_auf.xlsx"):
    return pd.read_excel(file_name, sheet_name="AUF")


def calculate_results(df, auf_d, **kwargs):
    excess_d = {}
    df2 = df.copy()

    fixed_price = kwargs.get("fixed_price", None)
    if fixed_price is not None:
        df2["PTF"] = fixed_price

    for key, value in auf_d.items():
        excess_d[key] = df2.apply(
            lambda row: (row["PTF"] - value) * row[key], axis=1
        ).sum()

    return excess_d


st.session_state["auf"] = {}

st.title("EPDK-EPIAS Azami Uzlaştırma Fiyatı Simülasyonu")
st.markdown(
    "Şubat 2022 kaynağa göre üretim ve PTF verilerini kullanarak farklı Azami Uzlaştırma Fiyatı senaryolarında Destekleme Bedeli Borç Tutarı (DBBT) ve Üretim Destekleme Tutarı (ÜDT) değerlerini hesaplayın. Metodoloji ve kaynaklar sayfanın altında belirtilmiştir. Herhangi bir sorumluluk kabul edilmemektedir."
)


st.sidebar.header("Azami Uzlaştırma Fiyatı")
st.session_state["calc"] = st.sidebar.button("Hesapla")

st.session_state["use_max_price"] = st.sidebar.checkbox(
    "PTF'yi tavan fiyat (" + str(st.session_state["max_price"]) + " TL) ile değiştir.",
    value=False,
)

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

st.header("Özet Veriler")
if st.session_state["calc"]:
    x_d = calculate_results(
        df=st.session_state["rawdf"],
        auf_d=st.session_state["auf"],
        fixed_price=(
            st.session_state["max_price"] if st.session_state["use_max_price"] else None
        ),
    )

    dbbt_val = sum([value if value > 0 else 0 for value in x_d.values()]) / 10 ** 6
    udt_val = sum([value if value < 0 else 0 for value in x_d.values()]) / 10 ** 6

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DBBT", str(round(dbbt_val, 2)) + "M TL", None)
    col2.metric("ÜDT", str(round(abs(udt_val), 2)) + "M TL", None)
    col3.metric(
        "GTŞ Payı",
        str(max(0, round(abs(abs(dbbt_val) - abs(udt_val)), 2))) + "M TL",
        None,
    )
    col4.metric(
        "Destek Katsayısı", str(min(1.0, round(dbbt_val / abs(udt_val), 4))), None
    )
    st.markdown(
        "*Not: Destek Katsayısı 1 TL ÜDT'ye hak kazanan üreticinin ne kadar destekleneceğini belirtmektedir. Toplam DBBT, toplam ÜDT'den düşük olduğu durumlarda oransal destekleme yapılmaktadır. Eğer DBBT, ÜDT'den yüksek ise aradaki fark mevzuat göreği Görevli Tedarik Şirketlerine (GTŞ) aktarılacaktır (GTŞ payı).*"
    )

    st.header("Kaynağa göre AUF kaynaklı Farklar")
    st.markdown(
        """Sıfırdan küçükse Üretim Destekleme Tutarı (ÜDT), büyükse Destekleme Bedeli Borç Tutarı (DBBT) olarak kabul edilebilir."""
    )
    st.json(x_d)
else:
    st.info("Değerleri görebilmek için lütfen sol menüden Hesapla düğmesine tıklayın.")


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

if st.session_state["use_max_price"]:
    st.info(
        "Bütün PTF değerleri hesaplamada tavan fiyat olan "
        + str(st.session_state["max_price"])
        + "TL/MWh ile değiştirilmiştir. PTF değerlerini kullanmak için sol menüden ilgili seçimi kaldırınız."
    )
st.dataframe(st.session_state["rawdf"])

st.header("Notlar")
st.markdown(
    """
+ Hesaplama metodolojisi Resmi Gazete'de paylaşılan [17 Mart 2022 tarihli 10866 sayılı EPDK Kurul Kararı](https://www.resmigazete.gov.tr/eskiler/2022/03/20220318-16.pdf)\'ndan alınmıştır. Sonraki mevzuatlarda metodoloji değişiklikleri varsa yansıtılmamıştır.
+ Şubat 2022'ye ait veriler [EPİAŞ Şeffaflık Platformu](https://seffaflik.epias.com.tr/)\'ndan alınmıştır.
+ İlgili metodolojiye ait olan hesaplamalar olabildiğince doğru bir şekilde yansıtılmaya çalışılmıştır ancak eksikler/yanlışlar olabilir.
+ Kendi veri setinizi kullanmak istiyorsanız kaynak veri seti dosyasını [indirip](https://github.com/berkorbay/st-auf-simulation/blob/main/epias_auf.xlsx?raw=true) değiştirerek sisteme yükleyebilirsiniz.
+ Üretim kaynakları olarak EPİAŞ Şeffaflık Platformu'ndaki UEVM başlıkları esas alınmıştır. Format tutarlılığı açısından isim değişikliği yapılmış olabilir.
+ Düşük üretim miktarına sahip bazı kaynaklar dahil edilmemiştir.
+ UEVM değerlerinden YEKDEM ve Lisanssız üretim verileri çıkarılmıştır. Güneş üretimi neredeyse tamamen YEKDEM ve Lisanssız üretim olduğu için hesaplamalara dahil edilmemektedir. Mevzuatta belirtilen diğer istisnalar (ör. yerli kömür, bazı ikili anlaşmalar) veri eksikliği sebebiyle düzenlenememiştir.
+ Veri ve koda ulaşmak için [Github](github.com/berkorbay/st-auf-simulation/) sayfasını ziyaret edebilirsiniz. 
+ Mevzuata göre desteklenmeye hak kazanan santraller eğer toplam DBBT, toplam ÜDT'ye eşit veya büyükse bütün desteği alabileceklerdir. Diğer durumda hak kazandıkları destek Destek Katsayısı ile çarpılarak bulunacaktır. Eğer ÜDT büyükse arada kalan fark GTŞlere aktarılacaktır.
"""
)
