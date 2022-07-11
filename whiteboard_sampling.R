library("dplyr", lib.loc = "/home/golah/Rpackages")

## Defining parameters
image_path = "/home/golah/images_roland/"

list_of_photos = list.files(path = image_path)
length_june_photos = length(list_of_photos)
train_ratio = 0.4
val_ratio = 0.1 
set.seed(123)

# Sampling, creating vectors containing the chosen image labels
train_photos = sample(list_of_photos, train_ratio * length_june_photos, replace = FALSE)
photos_without_train = anti_join(data.frame(col_name = list_of_photos), data.frame(col_name = train_photos))
val_photos = sample(photos_without_train[,1], val_ratio * length_june_photos, replace =  FALSE)
photos_test_only = anti_join(photos_without_train, data.frame(col_name = val_photos))
test_photos = photos_test_only[,1]

# Creating (new folders) with the chosen images
for(i in train_photos) {
  file.copy(from = paste(image_path, i, sep = ""), to = "/home/golah/COCO/images/train2017")
}

for(i in val_photos) {
file.copy(from = paste(image_path, i, sep = ""), to = "/home/golah/COCO/images/val2017")
}

for(i in test_photos) {
  file.copy(from = paste(image_path, i, sep = ""), to = "/home/golah/COCO/TEST")
}

