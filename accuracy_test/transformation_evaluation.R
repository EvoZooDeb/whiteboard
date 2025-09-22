# Load packages
library(dplyr)
library(ggplot2)

# Read data
old_low  = read.csv("01_old_low.csv")
old_high = read.csv("02_old_high.csv")
new_low  = read.csv("03_new_low.csv")
new_high = read.csv("04_new_high_control.csv")
new_high_coords = read.csv("transform_by_coords.csv") # Result of transformation via manual reference square coordinates

### Add ID column
old_low$board    = "old"
old_low$quality  = "low"
old_high$board   = "old"
old_high$quality = "high"
new_low$board    = "new"
new_low$quality  = "low" 
new_high$board   = "new"
new_high$quality = "high"

### Evaluate combined method
res_na = rbind(old_low, old_high, new_low, new_high)

# Evaluate seperate test groups
# 01 Old_low
#res_na = old_low

# 02 Old_high
#res_na = old_high

# 03 New_low
#res_na = new_low

# 04 New_high
#res_na = new_high

# 04 New_high with manual coordinates
#res_na = new_high_coords

# Remove index columns
res_na = res_na[-1]

# Remove NA rows
res = res_na[!is.na(res_na$X),]

# Create mes. error column, 1 cm = 10 pixel
res$error = (950 - res$Y)

# The highest negative error (shortening)
min_error = min(res$error)

# The highest positive error (lengthening)
max_error = max(res$error)

# The mean meas. error
mean_error = mean(res$error)

# Visualize meas. errors on a histogram. Red lines indicate +/- 5 cm threshold.
ggplot(res, aes(x = error)) +
  geom_histogram(binwidth = 10) +
  xlim(-100, 100) +
  geom_vline(aes(xintercept = -50), color = "red",size = 1) +
  geom_vline(aes(xintercept = 50), color = "red",size = 1)

# Visaluzie meas. error on a scatter plot
p = ggplot(res, aes(x = 1:234, y=error/10, color = quality, shape = board)) +
  geom_point() +
  ylim(-6, 6)  +
  scale_y_continuous(limits = c(-6, 6), breaks = seq(-5, 5, by = 1.25)) +
  ylab("Error in cm") +
  geom_hline(aes(yintercept = -5), color = "red", size = 0.5) +
  geom_hline(aes(yintercept = 5), color = "red", size = 0.5) +
  geom_hline(aes(yintercept = -3.75), color = "orange", size = 0.5) +
  geom_hline(aes(yintercept = 3.75), color = "orange", size = 0.5) +
  geom_hline(aes(yintercept = -2.5), color = "yellow", size = 0.5) +
  geom_hline(aes(yintercept = 2.5), color = "yellow", size = 0.5) +
  geom_hline(aes(yintercept = -1.25), color = "green", size = 0.5) +
  geom_hline(aes(yintercept = 1.25), color = "green", size = 0.5) +
  geom_hline(aes(yintercept = 0), color = "black", size = 0.5) +
  theme(axis.title.x=element_blank(),
       axis.text.x=element_blank(),
       axis.ticks.x=element_blank())
p
#ggsave("SFIG1.PNG", plot = p, units = "mm", )

### Creating "Zones"
# Abs. meas. error < 1.25 cm
zone_1 = nrow(res[abs(res$error) < 12.5,]) / nrow(res_na) 

# 1.25 cm <= Abs. meas. error < 2.5 cm
zone_2 = nrow(res[12.5 <= abs(res$error) & abs(res$error) < 25,]) / nrow(res_na) 

# 2.5 cm <= Abs. meas. error < 3.75 cm
zone_3 = nrow(res[25 <= abs(res$error) & abs(res$error) < 37.5,]) / nrow(res_na) 

# 3.75 cm <= Abs. meas. error < 5 cm
zone_4 = nrow(res[37.5 <= abs(res$error) & abs(res$error) < 50,]) / nrow(res_na) 

# Abs. meas. error > 5 cm
zone_5 = nrow(res[abs(res$error) >= 50,]) / nrow(res_na) 

# NA zone:
na_zone = 1 - (zone_1 + zone_2 + zone_3 + zone_4 + zone_5)

### Statistical analysis
## The effect of board renowation
# Data preparation
old_table_res = rbind(old_low, old_high)
old_table_res$table = "old"
  
new_table_res = rbind(new_low, new_high)
new_table_res$table = "new"

combined_table_res = rbind(old_table_res, new_table_res)
combined_table_res = combined_table_res[-1]
combined_table_res = combined_table_res[!is.na(combined_table_res$X),]
combined_table_res$error = (950 - combined_table_res$Y)

# Check for normal dist.
shapiro.test(combined_table_res$error[combined_table_res$table == "old"])
#hist(combined_table_res$error[combined_table_res$table == "old"])
# p < 0.05 non normal dist.
shapiro.test(combined_table_res$error[combined_table_res$table == "new"])
# p < 0.05 non normal dist. --> Wilcoxon-test

# Two-sample Wilcoxon-test
wilcox.test(combined_table_res$error[combined_table_res$table == "old"], combined_table_res$error[combined_table_res$table == "new"])
# p < 0.05 a significant difference between old and new board meas. errors

## Effect of image resolution combined
# Data preparation
low_resolution_res = rbind(old_low, new_low)
low_resolution_res$resolution = "low"

high_resolution_res = rbind(old_high, new_high)
high_resolution_res$resolution = "high"

combined_resolution_res = rbind(low_resolution_res, high_resolution_res)
combined_resolution_res = combined_resolution_res[-1]
combined_resolution_res = combined_resolution_res[!is.na(combined_resolution_res$X),]
combined_resolution_res$error = (950 - combined_resolution_res$Y)

# Check for normal dist.
shapiro.test(combined_resolution_res$error[combined_resolution_res$resolution == "low"])
# p > 0.05 normal dist.
shapiro.test(combined_resolution_res$error[combined_resolution_res$resolution == "high"])
# p > 0.05 normal dist. --> Two-sample t-test

# Variancie analysis
var.test(combined_resolution_res$error[combined_resolution_res$resolution == "low"], combined_resolution_res$error[combined_resolution_res$resolution == "high"])
# p < 0.05 variances differ --> Welch's t-test
t.test(combined_resolution_res$error[combined_resolution_res$resolution == "low"], combined_resolution_res$error[combined_resolution_res$resolution == "high"], var.equal = FALSE)
# p < 0.05 a significant difference between low and high resolution meas. errors