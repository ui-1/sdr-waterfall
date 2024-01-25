import numpy as np
import imageio
import math


def calculate_luma(pixel_rgba):
    return 0.2126*pixel_rgba[0] + 0.7152*pixel_rgba[1] + 0.0722*pixel_rgba[2]


def RGBA_to_LUMA(imagedata):
    return np.apply_along_axis(calculate_luma, 2, imagedata)


def repeat_lines(imagedata, samplerate, linetime):
    samples_per_line_for_1second = samplerate / imagedata.shape[1] * 2
    samples_per_line_for_linetime = samples_per_line_for_1second * linetime
    reps = math.ceil(samples_per_line_for_linetime)
    return np.repeat(imagedata, reps, axis=0) ** 2.


def image_padding(imagedata):
    width = imagedata.shape[1] * 2
    img_with_padding = np.zeros((imagedata.shape[0], width))
    img_with_padding[:, width//4:(width*3//4)] = imagedata
    return img_with_padding


def apply_ifft(imagedata):
    ifft = np.fft.ifft(np.fft.ifftshift(imagedata, axes=1), axis=1)
    ifft = ifft.flatten()
    ifft /= np.max(ifft)
    return ifft


def make_iq(imagedata, output):
    iq = np.zeros(2 * imagedata.size, dtype=np.float32)
    iq[0::2] = np.real(imagedata)
    iq[1::2] = np.imag(imagedata)
    with open(output, 'wb') as f:
        f.write(iq.tobytes())


def main(input_image, samplerate=192000, linetime=0.01, output='out.iq'):
    read = imageio.v3.imread(input_image)
    img = np.copy(read)

    img = img[::-1, ::-1, :]
    img = RGBA_to_LUMA(img)
    img = repeat_lines(img, samplerate, linetime)
    img = image_padding(img)
    img = apply_ifft(img)

    make_iq(img, output)


if __name__ == '__main__':
    main('lain.png', linetime=0.01, samplerate=48000)
