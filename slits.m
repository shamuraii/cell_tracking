%% Slit Processing
clear
clc
close all

%fname = 'D:\Research\Videos\20-2.avi';
%outf = 'D:\Research\Videos\output\20-2\';
fname = 'V4.avi';
outf = '';

%% Generate Slits

vid = vision.VideoFileReader(fname);

num_frames = 501;
slits_im = zeros(vid.info.VideoSize(2),num_frames);
for i=1:num_frames
   
   f = vid();
   f_gray = f(:,:,1);
   
   slit = f_gray(:,size(f,2)/2);
   slits_im(:,i) = slit;
   
end

imshow(slits_im,[]);

release(vid);

%% Binarization

% Filter and Subtract Mean
slit_f = imgaussfilt(slits_im,3);
s = mean(slit_f,2);
s_front = slit_f - repmat(s,1,size(slit_f,2));
%s_front = imgaussfilt(s_front,3);

% Get binary image from threshold
%s_gray = mat2gray(s_front);
s_gray = s_front;
s_bw = imbinarize(s_gray);
% Flip image if most pixels are white
if (mean(s_bw(:)) > 0.5)
    s_bw = imcomplement(s_bw);
end

%% Centroid Finding + Counting

% https://www.mathworks.com/help/images/ref/regionprops.html
% ^^^ Regionprops has MANY return options that could be useful
% EX: using the major/minor axis length + Orientation to estimate size/speed

%Get centroids
data = regionprops(s_bw,'centroid');
centroids = cat(1,data.Centroid);

% Display centroid results
figure(2);
imshow(s_bw);
figure(1);
hold on
plot(centroids(:,1),centroids(:,2),'y*')
hold off

% Round center locations to integer values
center_ints = round(centroids);

%% Gather Output Data
FPS = 35; % Based on camera properties

% Use a histogram for easy data manipulation
f3 = figure(3);
h = histogram(center_ints(:,1));

% CELLS PER FRAME
h.BinWidth = 1;
count_per_frame = h.Values;
f = getframe(f3);
imwrite(f.cdata,[outf, 'cells_per_frame.png']);

% CELLS PER SECOND
h.BinWidth = FPS;
count_per_sec = h.Values;
f = getframe(f3);
imwrite(f.cdata,[outf, 'cells_per_sec.png']);

% TOTAL CELLS PER SECOND
h.Normalization = 'cumcount';
cumcount_per_sec = h.Values;
f = getframe(f3);
imwrite(f.cdata,[outf, 'total_per_sec.png']);

