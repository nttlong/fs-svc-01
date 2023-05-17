import cv2
import matplotlib.pyplot as plt
Video = "/home/vmadmin/python/v6/file-service-02/temp-data/Red Dead Redemption.mp4"
cap=cv2.VideoCapture(Video)
# while (True):
#    ret,frame=cap.read()
#    cv2.imshow("video",frame)
#    # 在播放每一帧时，使用cv2.waitKey()设置适当的持续时间。如果设置的太低视频就会播放的非常快，如果设置的太高就会播放的很慢。通常情况下25ms就ok
#    if cv2.waitKey(1)&0xFF==ord('q'):
#        cv2.destroyAllWindows()
#        break
def Diff_img(img0, img):
  '''
  This function is designed for calculating the difference between two
  images. The images are convert it to an grey image and be resized to reduce the unnecessary calculating.
  '''
  # Grey and resize
  img0 =  cv2.cvtColor(img0, cv2.COLOR_RGB2GRAY)
  img =  cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  img0 = cv2.resize(img0, (320,200), interpolation = cv2.INTER_AREA)
  img = cv2.resize(img, (320,200), interpolation = cv2.INTER_AREA)
  # Calculate
  Result = (abs(img - img0)).sum()
  return Result
cap=cv2.VideoCapture(Video)
ret,frame0 = cap.read()

Result = []
Num = 0

# while (True):
#    print(Num)
#    ret,frame=cap.read()
#    #cv2.imshow("video",frame)
#    if Num > 0:
#     Result += [Diff_img(frame0, frame)]
#     frame0 = frame
#    Num += 1
#
#    if cv2.waitKey(25)&0xFF==ord('q'):
#        cv2.destroyAllWindows()
#        break

cap=cv2.VideoCapture(Video)
ret,frame0 = cap.read()

fps_c = cap.get(cv2.CAP_PROP_FPS)
Video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
Video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

fps = fps_c
size = (Video_w,Video_h)
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
out_put = f"/home/vmadmin/python/v6/file-service-02/temp-data/output.mp4"
videowriter = cv2.VideoWriter(out_put,fourcc,fps,size)



Result = []
Num = 0
read_ok = True
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
  """
  Call in a loop to create terminal progress bar
  @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      prefix      - Optional  : prefix string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
      length      - Optional  : character length of bar (Int)
      fill        - Optional  : bar fill character (Str)
      printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
  """
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + '-' * (length - filledLength)
  print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
  # Print New Line on Complete
  if iteration == total:
    print()
_prefxi_ =" "
msg =""
printProgressBar(iteration=0,length=100,total=length,printEnd=msg)
nf =0
while (read_ok):
  read_ok,frame=cap.read()
  if read_ok:

    #cv2.imshow("video",frame)
    if Num > 0:
      Diff = Diff_img(frame0, frame)
      Result += [Diff]
      frame0 = frame
      #5409507-----------------------------------------------------------------------------------------------| 3.2%

      if Diff > 8509507:
        videowriter.write(frame0)
        nf+=1
        msg = f'Num of frame {nf}'
        printProgressBar(iteration=Num,length=100,total=length)
  Num += 1


videowriter.release()