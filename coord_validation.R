# Validation script for the whiteboard corner coordinates
library(ggplot2)
library(dplyr)
library(rjson)
# ID of result
result_id = 43

# Loading the original coordinates
original_coords = read.csv("/home/eram/WHITEBOARD_PROJECT/validation_script/Results.csv")
original_coords = original_coords[c("X.1","Label","X", "Y")]
#original_coords$origin = "original"
original_coords$position = "left"
original_coords[original_coords["X.1"]%%2 == 0, "position"] = "right"
original_coords = original_coords[,-1]

# Loading the measurement results
top_left = read.csv(paste("/home/eram/WHITEBOARD_PROJECT/validation_script/top_left_",result_id, ".csv",sep =''), col.names = c("Label", "X", "Y"))
#top_left$origin = "calculated"
top_left$position = "left"

top_right = read.csv(paste("/home/eram/WHITEBOARD_PROJECT/validation_script/top_right_",result_id, ".csv",sep =''), col.names = c("Label", "X", "Y"))
#top_right$origin = "calculated"
top_right$position = "right"

# Binding the left and right corner
measured_coords = rbind(top_left, top_right)
measured_coords$X = as.numeric(sub("^\\[", " ", measured_coords$X))
measured_coords$Y = as.numeric(sub("\\]$", " ", measured_coords$Y))

# Mergint the data-tables
coords_df = left_join(measured_coords, original_coords, by = c("Label", "position"), keep = FALSE, suffix = c("_calculated", "_original"))
coords_df[coords_df[,"Label"] == "IMG_4908.JPG", ]

for(i in unique(coords_df$Label)){
print(coords_df[coords_df[,"Label"] == i, c('Label', "Y_calculated", "Y_original", "Y_error")])
}

# Plot the differences with scatterplot
coords_df %>%
  ggplot(aes(x = X_calculated, y = X_original, color = position))+
  ylim(0, 3000) +
  xlim(0, 3000) +
  geom_abline(intercept = 0, slope = 1) +
  geom_smooth() +
  geom_point()

coords_df %>%
  ggplot(aes(x = Y_calculated, y =Y_original, color = position))+
  ylim(0, 2000) +
  xlim(0, 2000) +
  geom_abline(intercept = 0, slope = 1) +
  geom_smooth() +
  geom_point()

# Calculate error for X and Y
coords_df = coords_df %>% mutate(X_error = X_original - X_calculated,
                     Y_error = Y_original - Y_calculated)

# Take the mean, meanabs value of the error
mean_xerr = mean(coords_df$X_error)
mean_yerr = mean(coords_df$Y_error)

abs_mean_xerr = mean(abs(coords_df$X_error))
abs_mean_yerr = mean(abs(coords_df$Y_error))

# Plot the distribution of error values on a histogram
ggplot(coords_df, aes(x = X_error, fill = position)) +
  geom_histogram(binwidth = 50)

ggplot(coords_df, aes(x = Y_error, fill = position)) +
  geom_histogram(binwidth = 50)

# See what happens if we remove outliers
mean_xerr_no = mean(coords_df[abs(coords_df$X_error) < 500, "X_error"])
mean_yerr_no = mean(coords_df[abs(coords_df$Y_error) < 500, "Y_error"])

abs_mean_xerr_no = mean(abs(coords_df[abs(coords_df$X_error) < 500, "X_error"]))
abs_mean_yerr_no = mean(abs(coords_df[abs(coords_df$Y_error) < 500, "Y_error"]))

# Outlier count
outliers = coords_df[abs(coords_df$X_error) > 500 | abs(coords_df$Y_error) > 500,]
outliers = unique(outliers$Label)

# Plot the differences with scatterplot
  ggplot(coords_df[abs(coords_df$X_error) < 500, ], aes(x = X_calculated, y = X_original, color = position))+
  ylim(0, 3000) +
  xlim(0, 3000) +
  geom_abline(intercept = 0, slope = 1) +
  geom_smooth() +
  geom_point()

  ggplot(coords_df[abs(coords_df$X_error) < 500, ],aes(x = Y_calculated, y =Y_original, color = position))+
  ylim(0, 2000) +
  xlim(0, 2000) +
  geom_abline(intercept = 0, slope = 1) +
  geom_smooth() +
  geom_point()
  
# Plot the distribution of error values on a histogram
ggplot(coords_df[abs(coords_df$X_error) < 500, ], aes(x = X_error, fill = position)) +
  geom_histogram(binwidth = 50)

ggplot(coords_df[abs(coords_df$Y_error) < 500, ], aes(x = Y_error, fill = position)) +
  geom_histogram(binwidth = 50)

results = list()
# Blur type, flag and threshold limits
results[["line"]]             = TRUE
results[["model"]]            = "converted_model_epoch_99.h5"
results[["1_edge_detection"]] = "median_7_00-200"
results[["2_edge_detection"]] = NA
results[["edge_correction"]]  = 0
results[["upper_range"]]      = "1-250-3"
results[["upper_width"]]      =  15
results[["left_range"]]       = "1-125-3+0-625"
results[["left_width"]]       =  48
results[["right_range"]]      = "1-125-3+0-625"
results[["right_width"]]      =  48
results[["template_match"]]   = "TM_CCOEFF"
results[["outlier_number"]]   = length(outliers)
results[["mean_xerr"]] = mean_xerr
results[["mean_yerr"]] = mean_yerr
results[["abs_mean_xerr"]] = abs_mean_xerr
results[["abs_mean_yerr"]] = abs_mean_yerr
results[["mean_xerr_no"]] = mean_xerr_no
results[["mean_yerr_no"]] = mean_yerr_no
results[["abs_mean_xerr_no"]] = abs_mean_xerr_no
results[["abs_mean_yerr_no"]] = abs_mean_yerr_no

# Save results
results_JS = toJSON(results, indent = 2)
fileConn = file(paste("/home/eram/WHITEBOARD_PROJECT/results/result_", result_id, ".json", sep = ''))
writeLines(results_JS, fileConn)
close(fileConn)
