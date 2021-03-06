from TOOLS import Functions

import cv2
import numpy as np
import math
# import argparse

class preprocess:
    def __init__(self):
        self = self

    def licensePlateDectiion(self,path):
        # this folder is used to save the image
        temp_folder = '/tmp/'

        # ap = argparse.ArgumentParser()
        # ap.add_argument("-i", "--image", type=str, required=True, help="path to image")
        # args = vars(ap.parse_args())

        img = cv2.imread(path)
        cv2.imshow('original', img)
        # cv2.imwrite(temp_folder + '1 - original.png', img)

        # hsv transform - value = gray image
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # hue, saturation, value = cv2.split(hsv)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # cv2.imshow('gray', value)
        # cv2.imwrite(temp_folder + '2 - gray.png', value)

        # kernel to use for morphological operations
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        # applying topHat/blackHat operations
        # topHat = cv2.morphologyEx(value, cv2.MORPH_TOPHAT, kernel)
        # blackHat = cv2.morphologyEx(value, cv2.MORPH_BLACKHAT, kernel)
        # cv2.imshow('topHat', topHat)
        # cv2.imshow('blackHat', blackHat)
        # cv2.imwrite(temp_folder + '3 - topHat.png', topHat)
        # cv2.imwrite(temp_folder + '4 - blackHat.png', blackHat)

        # add and subtract between morphological operations
        # add = cv2.add(value, topHat)
        # subtract = cv2.subtract(add, blackHat)
        # cv2.imshow('subtract', subtract)
        # cv2.imwrite(temp_folder + '5 - subtract.png', subtract)

        # applying gaussian blur on subtract image
        # blur = cv2.GaussianBlur(subtract, (5, 5), 0)
        gauss = cv2.GaussianBlur(gray, (3, 3), 1)
        # cv2.imshow('blur', blur)
        # cv2.imwrite(temp_folder + '6 - blur.png', blur)

        # thresholding
        # thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)
        thresh = cv2.adaptiveThreshold(gauss, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 9)
        cv2.imshow('thresh', thresh)
        # cv2.imwrite(temp_folder + '7 - thresh.png', thresh)

        # cv2.findCountours() function changed from OpenCV3 to OpenCV4: now it have only two parameters instead of 3
        cv2MajorVersion = cv2.__version__.split(".")[0]
        # check for contours on thresh
        if int(cv2MajorVersion) >= 4:
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        else:
            imageContours, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # get height and width
        height, width = thresh.shape

        # create a numpy array with shape given by threshed image value dimensions
        imageContours = np.zeros((height, width, 3), dtype=np.uint8)

        # list and counter of possible chars
        possibleChars = []
        countOfPossibleChars = 0

        # loop to check if any (possible) char is found
        for i in range(0, len(contours)):

            # draw contours based on actual found contours of thresh image
            cv2.drawContours(imageContours, contours, i, (255, 255, 255))

            # retrieve a possible char by the result ifChar class give us
            possibleChar = Functions.ifChar(contours[i])

            # by computing some values (area, width, height, aspect ratio) possibleChars list is being populated
            if Functions.checkIfChar(possibleChar) is True:
                countOfPossibleChars = countOfPossibleChars + 1
                possibleChars.append(possibleChar)

        cv2.imshow("contours", imageContours)
        # cv2.imwrite(temp_folder + '8 - imageContours.png', imageContours)

        imageContours = np.zeros((height, width, 3), np.uint8)

        ctrs = []

        # populating ctrs list with each char of possibleChars
        for char in possibleChars:
            ctrs.append(char.contour)

        # using values from ctrs to draw new contours
        cv2.drawContours(imageContours, ctrs, -1, (255, 255, 255))
        cv2.imshow("contoursPossibleChars", imageContours)
        cv2.imwrite(temp_folder + '9 - contoursPossibleChars.png', imageContours)

        plates_list = []
        listOfListsOfMatchingChars = []

        for possibleC in possibleChars:

            # the purpose of this function is, given a possible char and a big list of possible chars,
            # find all chars in the big list that are a match for the single possible char, and return those matching chars as a list
            def matchingChars(possibleC, possibleChars):
                listOfMatchingChars = []

                # if the char we attempting to find matches for is the exact same char as the char in the big list we are currently checking
                # then we should not include it in the list of matches b/c that would end up double including the current char
                # so do not add to list of matches and jump back to top of for loop
                for possibleMatchingChar in possibleChars:
                    if possibleMatchingChar == possibleC:
                        continue

                    # compute stuff to see if chars are a match
                    distanceBetweenChars = Functions.distanceBetweenChars(possibleC, possibleMatchingChar)

                    angleBetweenChars = Functions.angleBetweenChars(possibleC, possibleMatchingChar)

                    changeInArea = float(abs(possibleMatchingChar.boundingRectArea - possibleC.boundingRectArea)) / float(
                        possibleC.boundingRectArea)

                    changeInWidth = float(abs(possibleMatchingChar.boundingRectWidth - possibleC.boundingRectWidth)) / float(
                        possibleC.boundingRectWidth)

                    changeInHeight = float(abs(possibleMatchingChar.boundingRectHeight - possibleC.boundingRectHeight)) / float(
                        possibleC.boundingRectHeight)

                    # check if chars match
                    if distanceBetweenChars < (possibleC.diagonalSize * 5) and \
                            angleBetweenChars < 12.0 and \
                            changeInArea < 0.5 and \
                            changeInWidth < 0.8 and \
                            changeInHeight < 0.2:
                        listOfMatchingChars.append(possibleMatchingChar)

                return listOfMatchingChars


            # here we are re-arranging the one big list of chars into a list of lists of matching chars
            # the chars that are not found to be in a group of matches do not need to be considered further
            listOfMatchingChars = matchingChars(possibleC, possibleChars)

            listOfMatchingChars.append(possibleC)

            # if current possible list of matching chars is not long enough to constitute a possible plate
            # jump back to the top of the for loop and try again with next char
            if len(listOfMatchingChars) < 3:
                continue

            # here the current list passed test as a "group" or "cluster" of matching chars
            listOfListsOfMatchingChars.append(listOfMatchingChars)

            # remove the current list of matching chars from the big list so we don't use those same chars twice,
            # make sure to make a new big list for this since we don't want to change the original big list
            listOfPossibleCharsWithCurrentMatchesRemoved = list(set(possibleChars) - set(listOfMatchingChars))

            recursiveListOfListsOfMatchingChars = []

            for recursiveListOfMatchingChars in recursiveListOfListsOfMatchingChars:
                listOfListsOfMatchingChars.append(recursiveListOfMatchingChars)

            break

        imageContours = np.zeros((height, width, 3), np.uint8)

        for listOfMatchingChars in listOfListsOfMatchingChars:
            contoursColor = (255, 0, 255)

            contours = []

            for matchingChar in listOfMatchingChars:
                contours.append(matchingChar.contour)

            cv2.drawContours(imageContours, contours, -1, contoursColor)

        # cv2.imshow("finalContours", imageContours)
        # cv2.imwrite(temp_folder + '10 - finalContours.png', imageContours)

        for listOfMatchingChars in listOfListsOfMatchingChars:
            possiblePlate = Functions.PossiblePlate()

            # sort chars from left to right based on x position
            listOfMatchingChars.sort(key=lambda matchingChar: matchingChar.centerX)

            # calculate the center point of the plate
            plateCenterX = (listOfMatchingChars[0].centerX + listOfMatchingChars[len(listOfMatchingChars) - 1].centerX) / 2.0
            plateCenterY = (listOfMatchingChars[0].centerY + listOfMatchingChars[len(listOfMatchingChars) - 1].centerY) / 2.0

            plateCenter = plateCenterX, plateCenterY

            # calculate plate width and height
            plateWidth = int((listOfMatchingChars[len(listOfMatchingChars) - 1].boundingRectX + listOfMatchingChars[
                len(listOfMatchingChars) - 1].boundingRectWidth - listOfMatchingChars[0].boundingRectX) * 1.3)

            totalOfCharHeights = 0

            for matchingChar in listOfMatchingChars:
                totalOfCharHeights = totalOfCharHeights + matchingChar.boundingRectHeight

            averageCharHeight = totalOfCharHeights / len(listOfMatchingChars)

            plateHeight = int(averageCharHeight * 1.5)

            # calculate correction angle of plate region
            opposite = listOfMatchingChars[len(listOfMatchingChars) - 1].centerY - listOfMatchingChars[0].centerY

            hypotenuse = Functions.distanceBetweenChars(listOfMatchingChars[0],
                                                        listOfMatchingChars[len(listOfMatchingChars) - 1])
            correctionAngleInRad = math.asin(opposite / hypotenuse)
            correctionAngleInDeg = correctionAngleInRad * (180.0 / math.pi)

            # pack plate region center point, width and height, and correction angle into rotated rect member variable of plate
            possiblePlate.rrLocationOfPlateInScene = (tuple(plateCenter), (plateWidth, plateHeight), correctionAngleInDeg)

            # get the rotation matrix for our calculated correction angle
            rotationMatrix = cv2.getRotationMatrix2D(tuple(plateCenter), correctionAngleInDeg, 1.0)

            height, width, numChannels = img.shape

            # rotate the entire image
            imgRotated = cv2.warpAffine(img, rotationMatrix, (width, height))

            # crop the image/plate detected
            imgCropped = cv2.getRectSubPix(imgRotated, (plateWidth, plateHeight), tuple(plateCenter))

            # copy the cropped plate image into the applicable member variable of the possible plate
            possiblePlate.Plate = imgCropped

            # populate plates_list with the detected plate
            if possiblePlate.Plate is not None:
                plates_list.append(possiblePlate)

            # draw a ROI on the original image
            for i in range(0, len(plates_list)):
                # finds the four vertices of a rotated rect - it is useful to draw the rectangle.
                p2fRectPoints = cv2.boxPoints(plates_list[i].rrLocationOfPlateInScene)

                # roi rectangle colour
                rectColour = (0, 255, 0)

                cv2.line(imageContours, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), rectColour, 2)
                cv2.line(imageContours, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), rectColour, 2)
                cv2.line(imageContours, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), rectColour, 2)
                cv2.line(imageContours, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), rectColour, 2)

                cv2.line(img, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), rectColour, 2)
                cv2.line(img, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), rectColour, 2)
                cv2.line(img, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), rectColour, 2)
                cv2.line(img, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), rectColour, 2)

                # cv2.imshow("detected", imageContours)
                # cv2.imwrite(temp_folder + '11 - detected.png', imageContours)

                cv2.imshow("detectedOriginal", img)
                # cv2.imwrite(temp_folder + '12 - detectedOriginal.png', img)

                # cv2.imshow("plate", plates_list[i].Plate)
                # cv2.imwrite(temp_folder + '13 - plate.png', plates_list[i].Plate)

        cv2.waitKey(0)

    def licensePlateDectiionV2(self,path):
        # 读取图片
        rawImage = cv2.imread(path)
        # 高斯模糊，将图片平滑化，去掉干扰的噪声
        image = cv2.GaussianBlur(rawImage, (5, 5), 0)
        # 图片灰度化
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Sobel算子（X方向）
        Sobel_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
        # Sobel_y = cv2.Sobel(image, cv2.CV_16S, 0, 1)
        absX = cv2.convertScaleAbs(Sobel_x)  # 转回uint8
        # absY = cv2.convertScaleAbs(Sobel_y)
        # dst = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
        image = absX
        # 二值化：图像的二值化，就是将图像上的像素点的灰度值设置为0或255,图像呈现出明显的只有黑和白
        ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
        # 闭操作：闭操作可以将目标区域连成一个整体，便于后续轮廓的提取。
        kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 5))
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernelX)
        # 膨胀腐蚀(形态学处理)
        kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
        kernelY = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 19))
        image = cv2.dilate(image, kernelX)
        image = cv2.erode(image, kernelX)
        image = cv2.erode(image, kernelY)
        image = cv2.dilate(image, kernelY)
        # 平滑处理，中值滤波
        image = cv2.medianBlur(image, 15)
        # 查找轮廓
        contours, w1 = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for item in contours:
            rect = cv2.boundingRect(item)
            x = rect[0]
            y = rect[1]
            weight = rect[2]
            height = rect[3]
            if weight > (height * 2):
                # 裁剪区域图片
                chepai = rawImage[y:y + height, x:x + weight]
                cv2.imshow('chepai'+str(x), chepai)

        # 绘制轮廓
        image = cv2.drawContours(rawImage, contours, -1, (0, 0, 255), 3)
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def onaptivethreshold(self, x):
        value = cv2.getTrackbarPos("value", "Threshold")
        if(value < 3):
            value = 3
        if(value % 2 == 0):
            value = value + 1
        args = cv2.adaptiveThreshold(self.gauss, self.maxvalue, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, value, 9)
        gaus = cv2.adaptiveThreshold(self.gauss, self.maxvalue, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, value, 9)
        # thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)
        cv2.imshow("Args", args)
        cv2.imshow("Gaus", gaus)

    def testThreshold(self, path):
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        cv2.imshow('gray1', gray)
        cv2.imshow('gray2', value)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        topHat = cv2.morphologyEx(value, cv2.MORPH_TOPHAT, kernel)
        blackHat = cv2.morphologyEx(value, cv2.MORPH_BLACKHAT, kernel)
        add = cv2.add(value, topHat)
        subtract = cv2.subtract(add, blackHat)
        self.gauss = cv2.GaussianBlur(gray, (3, 3), 1)
        # self.gauss = cv2.GaussianBlur(subtract, (5, 5), 0)
        self. maxvalue = 255

        cv2.namedWindow("Threshold")
        cv2.createTrackbar("value", "Threshold", 0, 80, self.onaptivethreshold)
        cv2.imshow("Threshold", img)
        cv2.waitKey(0)

if __name__ == '__main__':
    path = '/home/nhydev/github/ai/nhyai/backend/api/preprocess/images/17.png'
    # path = '/var/www/gallery/media/videos/capture_out_images/5cfe084a-31e4-11ea-bf2d-408d5c891351/37.jpg'
    preprocess().licensePlateDectiion(path)
    # preprocess().testThreshold(path)