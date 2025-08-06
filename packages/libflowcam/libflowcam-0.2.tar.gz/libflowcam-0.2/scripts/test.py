from libflowcam import ROIReader

# A Sample, with some bigger copepods
sample = ROIReader("testdata/flowcam_polina_pontoon_1807_r1/flowcam_polina_pontoon_1807_r1.csv", verbose=True)
print(str(len(sample.rois)) + " ROIs") # Should be 137015 ROIs

sorted_rois = sorted(sample.rois, key=lambda x: x.width * x.height, reverse = True)

for roi in sorted_rois[:32]: # Gives back the 30 biggest plankton
    roi.image.save("testout/flowcam_polina_pontoon_1807_r1_" + str(roi.index) + ".png")
