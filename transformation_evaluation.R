# Csomagok betöltése
library(dplyr)
library(ggplot2)

# Adat betöltése
old_low  = read.csv("results_01_04.csv")
old_high = read.csv("results_02_07.csv")
new_low  = read.csv("results_03_02.csv")
new_high = read.csv("results_04_03.csv")

### Kombinált módszer kiértékelése esetén
res_na = rbind(old_low, old_high, new_low, new_high)

# Külön csopotok kiértékelése esetén
# 01 Old_low
#res_na = old_low

# 02 Old_high
#res_na = old_high

# 03 New_low
#res_na = new_low

# 04 New_high
#res_na = new_high

# Index oszlop eltávolítása
res_na = res_na[-1]

# NA sorok eltávolítása
res = res_na[!is.na(res_na$X),]

# Hiba oszlop létrehozása, 1 cm = 10 pixel, tehát a felső vonal elméletileg Y tengely 950 pixelnél van.
res$error = (950 - res$Y)

# A legnagyobb hiba negatív irányban (rövidülés):
min_error = min(res$error)

# A legnagyobb hiba pozitív irányban (hosszabítás):
max_error = max(res$error)

# A módszer átlagos hibája
mean_error = mean(res$error)

# A hibák ábrázolása hisztogramon, piros vonalak jelzik a +/- 5 cm-es hibahatárt.
ggplot(res, aes(x = error)) +
  geom_histogram(binwidth = 10) +
  xlim(-100, 100) +
  geom_vline(aes(xintercept = -50), color = "red",size = 1) +
  geom_vline(aes(xintercept = 50), color = "red",size = 1)

# Hibák ábrázolása scatterplottal
plot(res$error/10,pch=19, ylim = c(-6,6), ylab = "Error in cm")
abline(h=0)
# Piros vonal +/- 5 cm
abline(h=5, col  = "red")
abline(h=-5, col  = "red")
# Narancssárga vonal +/- 3.75 cm
abline(h=3.75, col  = "orange")
abline(h=-3.75, col  = "orange")
# Citromsárga vonal +/- 2.50 cm
abline(h=2.50, col  = "yellow")
abline(h=-2.50, col  = "yellow")
# Zöld vonak +/- 1.25 cm
abline(h=1.25, col  = "green")
abline(h=-1.25, col  = "green")


# Címkézni, hogy negatív, vagy pozitív a hiba
#for(i in 1:length(res$error)){
#  if(res$error[i] < 0){
#    res$precursor[i] = "negative"
#  }
#  else{
#    res$precursor[i] = "positive"
#  }
#}

# Eredmények ahol az abs. hiba < 1.25 cm:
zone_1 = nrow(res[abs(res$error) < 12.5,]) / nrow(res_na) 

# Eredmények ahol: 1.25 cm <= abs. hiba < 2.5 cm:
zone_2 = nrow(res[12.5 <= abs(res$error) & abs(res$error) < 25,]) / nrow(res_na) 

# Eredmények ahol: 2.5 cm <= abs. hiba < 3.75 cm:
zone_3 = nrow(res[25 <= abs(res$error) & abs(res$error) < 37.5,]) / nrow(res_na) 

# Eredmények ahol: 3.75 cm <= abs. hiba < 5 cm:
zone_4 = nrow(res[37.5 <= abs(res$error) & abs(res$error) < 50,]) / nrow(res_na) 

# Eredmények ahol az abs. hiba > 5 cm:
zone_5 = nrow(res[abs(res$error) >= 50,]) / nrow(res_na) 

# Nem leolvasható eredmények:
na_zone = 1 - (zone_1 + zone_2 + zone_3 + zone_4 + zone_5)

### Eredmények kiértékelése
## Tábla "újítás" hatása
# Adatelőkészítés
old_table_res = rbind(old_low, old_high)
old_table_res$table = "old"
  
new_table_res = rbind(new_low, new_high)
new_table_res$table = "new"

combined_table_res = rbind(old_table_res, new_table_res)
combined_table_res = combined_table_res[-1]
combined_table_res = combined_table_res[!is.na(combined_table_res$X),]
combined_table_res$error = (950 - combined_table_res$Y)

# Normalitás vizsgálata
shapiro.test(combined_table_res$error[combined_table_res$table == "old"])
#hist(combined_table_res$error[combined_table_res$table == "old"])
# p > 0.05 normál eloszlás
shapiro.test(combined_table_res$error[combined_table_res$table == "new"])
# p < 0.05 nem normál eloszlás --> Wilcoxon-próba
# Kétmintás Wilcoxon-próba
wilcox.test(combined_table_res$error[combined_table_res$table == "old"], combined_table_res$error[combined_table_res$table == "new"])
# p < 0.05 a két tábla típus között szignifikáns különbség van

## Felbontás hatásának vizsgálata összesítve
# Adatelőkészítés
low_resolution_res = rbind(old_low, new_low)
low_resolution_res$resolution = "low"

high_resolution_res = rbind(old_high, new_high)
high_resolution_res$resolution = "high"

combined_resolution_res = rbind(low_resolution_res, high_resolution_res)
combined_resolution_res = combined_resolution_res[-1]
combined_resolution_res = combined_resolution_res[!is.na(combined_resolution_res$X),]
combined_resolution_res$error = (950 - combined_resolution_res$Y)

# Normalitás vizsgálata
shapiro.test(combined_resolution_res$error[combined_resolution_res$resolution == "low"])
# p < 0.05 nem normál eloszlás --> Wilcoxon-próba
shapiro.test(combined_resolution_res$error[combined_resolution_res$resolution == "high"])
# p > 0.05 normál eloszlás
# Kétmintás Wilcoxon-próba
wilcox.test(combined_resolution_res$error[combined_resolution_res$resolution == "low"], combined_resolution_res$error[combined_resolution_res$resolution == "high"])
# p > 0.05 a két felbontás között nincs szignifikáns különbség (old_high nagy hibáinak nagy a torzító hatása)

## Felbontás hatásának vizsgálata régi táblánál
# Adatelőkészítés
old_low_resolution_res  = old_low
old_low_resolution_res$resolution = "low"

old_high_resolution_res = old_high
old_high_resolution_res$resolution = "high"

old_resolution_res = rbind(old_low_resolution_res, old_high_resolution_res)
old_resolution_res = old_resolution_res[-1]
old_resolution_res = old_resolution_res[!is.na(old_resolution_res$X),]
old_resolution_res$error = (950 - old_resolution_res$Y)

# Normalitás vizsgálata
shapiro.test(old_resolution_res$error[old_resolution_res$resolution == "low"])
# p < 0.05 nem normál eloszlás --> Wilcoxon-próba
shapiro.test(old_resolution_res$error[old_resolution_res$resolution == "high"])
# p > 0.05 normál eloszlás
# Kétmintás Wilcoxon-próba
wilcox.test(old_resolution_res$error[old_resolution_res$resolution == "low"], old_resolution_res$error[old_resolution_res$resolution == "high"])
# p > 0.05 a két felbontás között nincs szignifikáns különbség (old_high nagy hibáinak nagy a torzító hatása)

## Felbontás hatásának vizsgálata új táblánál
# Adatelőkészítés
new_low_resolution_res  = new_low
new_low_resolution_res$resolution = "low"

new_high_resolution_res = new_high
new_high_resolution_res$resolution = "high"

new_resolution_res = rbind(new_low_resolution_res, new_high_resolution_res)
new_resolution_res = new_resolution_res[-1]
new_resolution_res = new_resolution_res[!is.na(new_resolution_res$X),]
new_resolution_res$error = (950 - new_resolution_res$Y)

# Normalitás vizsgálata
shapiro.test(new_resolution_res$error[new_resolution_res$resolution == "low"])
# p > 0.05 normál eloszlás
shapiro.test(new_resolution_res$error[new_resolution_res$resolution == "high"])
# p > 0.05 normál eloszlás --> Kétmintás T-próba

# Variancia vizsgálata
var.test(new_resolution_res$error[new_resolution_res$resolution == "low"], new_resolution_res$error[new_resolution_res$resolution == "high"])
# p < 0.05 két csoport varianciája nem egyezik --> Welch próba
# Kétmintás Welch-próba
t.test(new_resolution_res$error[new_resolution_res$resolution == "low"], new_resolution_res$error[new_resolution_res$resolution == "high"], var.equal = F)
# p > 0.05 a két felbontás között nincs szignifikáns különbség