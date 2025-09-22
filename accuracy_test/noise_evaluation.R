# Load packages
library(dplyr)
library(ggplot2)

# Read data
# Control
orig_control  = read.csv("04_new_high_control.csv")
new_high_coords = read.csv("transform_by_coords.csv")
cpu_inference = read.csv("cpu_inference.csv")
gimp_control  = read.csv("gimp_control.csv")

# Full cover
red_cover    = read.csv("red_cover.csv")
blue_cover   = read.csv("blue_cover.csv")
purple_cover = read.csv("purple_cover.csv")

# Vertical
red_vertical     = read.csv("red_vertical.csv")
blue_vertical    = read.csv("blue_vertical.csv")
purple_vertical  = read.csv("purple_vertical.csv")

# Horizontal
red_horizontal     = read.csv("red_horizontal.csv")
blue_horizontal    = read.csv("blue_horizontal.csv")
purple_horizontal  = read.csv("purple_horizontal.csv")

#Scattered
red_scattered     = read.csv("red_scattered.csv")
blue_scattered    = read.csv("blue_scattered.csv")
purple_scattered  = read.csv("purple_scattered.csv")                            

### Evaluate combined method
res_na = rbind(orig_control, gimp_control, red_cover, blue_cover, purple_cover, red_vertical, blue_vertical, purple_vertical,
               red_horizontal, blue_horizontal, purple_horizontal, red_scattered, blue_scattered, purple_scattered)

# Evaluate seperate groups
# orig_control
res_na = orig_control

# CPU inference
res_na = cpu_inference

# gimp_control
res_na = gimp_control

# red horizontal
res_na = red_horizontal

# blue horizontal
res_na = blue_horizontal

# purple horizontal
res_na = purple_horizontal

# red vertical
res_na = red_vertical

# blue vertical
res_na = blue_vertical

# purple vertical
res_na = purple_vertical

# red scattered
res_na = red_scattered

# blue scattered
res_na = blue_scattered

# purple scattered
res_na = purple_scattered

# red_cover
res_na = red_cover

# blue_cover
res_na = blue_cover

# purple_cover
res_na = purple_cover

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
  geom_histogram(binwidth = 12.5) +
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
determine_noise_effect = function(control_data, noise_data){
  control_data$noise  = deparse(substitute(control_data))
  noise_data$noise    = deparse(substitute(noise_data))
  combined_data       = rbind(control_data, noise_data)
  combined_data       = combined_data[-1]
  combined_data       = combined_data[!is.na(combined_data$X),]
  combined_data$error = (950 - combined_data$Y)

  # Check for normal dist.
  control   = combined_data$error[combined_data$noise == unique(control_data$noise)]
  noise     = combined_data$error[combined_data$noise == unique(noise_data$noise)]
  noise_string = unique(noise_data$noise)
  p_control = shapiro.test(control)[2]
  p_noise   = shapiro.test(noise)[2]
  if(p_control > 0.05 && p_noise > 0.05){
    print("Normal distribution: T-test")
    # F-test
    if(var.test(control, noise)[3] > 0.05){
      print("Variances do not differ: Student's T-test")
      print(t.test(control, noise, var.equal = TRUE)[3])
      if(t.test(control, noise, var.equal = TRUE)[3] > 0.05){
        print(paste0(noise_string, ": p > 0.05: Not significant effect size."))
      }
      else{
        print(paste0(noise_string, ": p < 0.05: Significant effect size."))
      }
    }
    else{
      print("Variances differ: Welch's T-test")
      print(t.test(control, noise, var.equal = FALSE)[3])
      if(t.test(control, noise, var.equal = FALSE)[3] > 0.05){
        print(paste0(noise_string, ": p > 0.05: Not significant effect size."))
      }
      else{
        print(paste0(noise_string, ": p < 0.05: Significant effect size."))
      }
    }
  }
  else{
    print("Not normal distribution: Wilcox's test")
    print(wilcox.test(control, noise, var.equal = FALSE)[3])
    if(wilcox.test(control, noise, var.equal = FALSE)[3] > 0.05){
      print(paste0(noise_string, ": p > 0.05: Not significant effect size."))
    }
    else{
      print(paste0(noise_string, ": p < 0.05: Significant effect size."))
    }
  }
}

determine_noise_effect(orig_control, new_high_coords)
determine_noise_effect(orig_control, cpu_inference)
determine_noise_effect(orig_control, gimp_control)
determine_noise_effect(gimp_control, red_horizontal)
determine_noise_effect(gimp_control, blue_horizontal)
determine_noise_effect(gimp_control, purple_horizontal)
determine_noise_effect(gimp_control, red_vertical)
determine_noise_effect(gimp_control, blue_vertical)
determine_noise_effect(gimp_control, purple_vertical)
determine_noise_effect(gimp_control, red_scattered)
determine_noise_effect(gimp_control, blue_scattered)
determine_noise_effect(gimp_control, purple_scattered)
determine_noise_effect(gimp_control, red_cover)
determine_noise_effect(gimp_control, blue_cover)
determine_noise_effect(gimp_control, purple_cover)



