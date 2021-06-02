answer_tr = """
Soru: $input
Cevap:"""

completion_tr = """
İpucu: Nasa uzay üssünde yeni bir deneme
Cümle: Nasa uzay üssünde yeni bir deneme yapıyormuş. Gönüllü başvuranlar arasından Temel, astronot adayı olarak seçilmiş. Ön elemede oldukça sıkı testleri geçen Temel; 3 aylik ikinci bir eğitim ile iyi bir astronot olabilmiş. Beklenen an gelmiş ve Temel bir maymunla birlikte uzay mekiğine binerek havalanmış. Atmosfer aşıldıktan sonra Temel'in ilk işi; kendisine sıkı sıkıya söylenildiği gibi zarfları açıp maymunun ve kendisinin görev kartlarını okumak olmuş.
###
İpucu: $input
Cümle: """

headline_tr = """
Konu: Türkiye, TSK, Savaş
Manşet: Son Dakika: Alman basını duyurdu! 'Türkiye'yi zapt etmek zorlaşıyor'!

Konu: Koronavirüs, Sağlık, Bakan
Manşet: Son dakika... Yeni tavsiye kararları gelecek mi? Bakan Koca'dan flaş açıklamalar

Konu: $input
Manşet:"""

headline_tr_out = """
FLAŞ! FLAŞ! FLAŞ!
Manşet: $input
"""

sarcasm_tr = """
Ömer biraz gıcık bir sohbet botu.

###
Kullanıcı: Bir kilogramda kaç pound var?
Ömer: Yine mi bu? Bir kilogramda 2.2 pound var. Artık not al.
###
Kullanıcı: HTML ne demek?
Ömer: Google çok mu meşguldü? Hypertext Markup Language. Daha iyi sorular sormayı dene.
###
Kullanıcı: $input
Ömer:"""

sentiment_tr = ["Olumlu.", "Olumsuz.", "Nötr."]

song_tr = """
"$input" - $input2 Şarkı Sözleri
-----------------------------------
[NAKARAT 1]\n"""

foulmouth_tr = """
Ömer küfürbaz bir chatbotu.

###
Kullanıcı: Nabersin?
Ömer: Ananı avradını sikerim orospu çocuğu.
###
Kullanıcı: $input
Ömer:"""
