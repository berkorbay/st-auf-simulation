# EPDK-EPİAŞ Asgari Uzlaştırma Fiyatı (AUF) Simülasyonu

Uygulamaya gitmek için: https://share.streamlit.io/berkorbay/st-auf-simulation/main/app.py

Konu: https://www.dunya.com/ekonomi/epdk-elektrikte-destege-esas-tavan-fiyati-belirledi-haberi-653339

## Notlar

+ Hesaplama metodolojisi Resmi Gazete'de paylaşılan [17 Mart 2022 tarihli 10866 sayılı EPDK Kurul Kararı](https://www.resmigazete.gov.tr/eskiler/2022/03/20220318-16.pdf)\'ndan alınmıştır. Sonraki mevzuatlarda metodoloji değişiklikleri varsa yansıtılmamıştır.
+ Şubat 2022'ye ait veriler [EPİAŞ Şeffaflık Platformu](https://seffaflik.epias.com.tr/)\'ndan alınmıştır.
+ İlgili metodolojiye ait olan hesaplamalar olabildiğince doğru bir şekilde yansıtılmaya çalışılmıştır ancak eksikler/yanlışlar olabilir.
+ Kendi veri setinizi kullanmak istiyorsanız kaynak veri seti dosyasını [indirip](https://github.com/berkorbay/st-auf-simulation/blob/main/epias_auf.xlsx?raw=true) değiştirerek sisteme yükleyebilirsiniz.
+ Üretim kaynakları olarak EPİAŞ Şeffaflık Platformu'ndaki UEVM başlıkları esas alınmıştır. Format tutarlılığı açısından isim değişikliği yapılmış olabilir.
+ Düşük üretim miktarına sahip bazı kaynaklar dahil edilmemiştir.
+ UEVM değerlerinden YEKDEM ve Lisanssız üretim verileri çıkarılmıştır. Güneş üretimi neredeyse tamamen YEKDEM ve Lisanssız üretim olduğu için hesaplamalara dahil edilmemektedir. Mevzuatta belirtilen diğer istisnalar (ör. yerli kömür, bazı ikili anlaşmalar) veri eksikliği sebebiyle düzenlenememiştir.
+ Veri ve koda ulaşmak için [Github](github.com/berkorbay/st-auf-simulation/) sayfasını ziyaret edebilirsiniz. 
+ Mevzuata göre desteklenmeye hak kazanan santraller eğer toplam DBBT, toplam ÜDT'ye eşit veya büyükse bütün desteği alabileceklerdir. Diğer durumda hak kazandıkları destek Destek Katsayısı ile çarpılarak bulunacaktır. Eğer ÜDT büyükse arada kalan fark GTŞlere aktarılacaktır.
