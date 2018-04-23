# DigiCon

# Readme

## Contents

1 Introduction 1

2 Requirements and dependencies 2
2.1 Hardware and OS........................... 2
2.2 Software dependencies........................ 2
2.2.1 Linux packages........................ 2
2.2.2 Python packages....................... 2

3 Installation 2
3.1 Installing using make......................... 2
3.2 Running the software......................... 3

4 User Manual 4

## 1 Introduction

The objective of DigiCon is that let allow a doctor to write his prescriptions the
conventional way (i.e., using their pen and paper). From the scanned version
of the prescription, a handwritten text recognition is followed to capture the
data (name of the patient, symptoms, findings, prescription of medicine, tests,
advice, etc.) written by the doctor. Since, the accuracy rate of the state-of- the-
art hand written character reorganization is not still up to the acceptable level,
we propose to apply an error correction mechanism to reduce the errors. The
solution does not oppose the age-old convention and affordable as it is mostly
a software solution with a minimum hardware requirement.


## 2 Requirements and dependencies

### 2.1 Hardware and OS

- Display resolution of minimum 1024x
- Ubuntu 14.04 LTS
- An internet connection

### 2.2 Software dependencies

2.2.1 Linux packages

- pip
- scipy

2.2.2 Python packages

- reportlab
- qdarkstyle
- requests

## 3 Installation

### 3.1 Installing using make

The software provided has initially the following directory structure.

```
Figure 1: Directory structure of provided software
```
- If you’re running the software behind a proxy make sure to set the proxy re-
    lated environment variables and also set HTTP, HTTPS proxies in ubuntu
    System Settings>Network>Network proxy
1 $ export httpproxy=” http : / / 1 7 2. 1 6. 2. 3 0: 80 8 0 ”
2 $ export httpsproxy=” https : / / 1 7 2. 1 6. 2. 3 0 : 8 08 0 ”
- Open a terminal and navigate to the digicon directory. Running ls com-
    mand in that directory should give the following output:
1 $ l s
2 digicon. tar. gz makefile


- Run make install to install the software. When asked for user password
    enter the password.
1 $ make i n s t a l l

```
After the install finishes the directory structure should look like this.
```
```
Figure 2: Directory structure after installation
```
### 3.2 Running the software

```
To run the software simply run ”make run” command in the terminal inside
digicon directory and a window will open. Instruction on how to use the software
is in the User Manual section.
```
1 $ make run


```
Figure 3: Window on running the software
```
## 4 User Manual

- To run the software simply run ”make run” command in the terminal
    inside digicon directory and a window will open. Instruction on how to
    use the software is in the User Manual section.
1 $ make run

```
Figure 4: Window on running the software
```
- When user opens the software, the user is provided with an option to open
    a picture. Either click the button or use shortcut Ctrl + O to open an
    image. A file browser appears. Choose an image.


```
Figure 5: Window to open an image
```
- After selecting the image, the software shows a preview of the image chosen
    and a button to proceed to process. To process the image click on process.

```
Figure 6: Window after choosing an image
```
- The progress bar shows how much processing is left. After a couple min-
    utes the processing is complete and another window will appear.


```
Figure 7: Window during processing the prescription
```
- The new window shows the results of each intermediate step of the pro-
    cessing. There are a total of 5 stages. Press N or P to see result of next
    pr previous step.


Figure 8: Window after processing finishes


```
Figure 9: The intermediate outputs(navigate with N/P key)
```
- The digicon/temp/ directory structure after running is as follows:

```
Figure 10: Directory structure after running the software
```
```
The document output is available in digicon/output/intermediateImgs/re-
sult.pdf
```

Figure 11: Final output


