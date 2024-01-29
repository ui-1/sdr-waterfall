import numpy as np
import imageio
import math


def rgba_to_luma(img: np.ndarray) -> np.ndarray:
    # https://en.wikipedia.org/wiki/Luma_(video)#Use_of_relative_luminance
    return np.apply_along_axis(lambda rgba: 0.2126*rgba[0] + 0.7152*rgba[1] + 0.0722*rgba[2], 2, img)


def repeat_lines(img: np.ndarray, samplerate: int, linetime: float) -> np.ndarray:
    samples_per_line_for_1second: float = samplerate / img.shape[1] * 2
    samples_per_line_for_linetime: float = samples_per_line_for_1second * linetime
    reps: int = math.ceil(samples_per_line_for_linetime)
    return np.repeat(img, reps, axis=0) ** 2.


def image_padding(img: np.ndarray) -> np.ndarray:
    padded_width: int = img.shape[1] * 2
    img_with_padding: np.ndarray = np.zeros((img.shape[0], padded_width))
    img_with_padding[:, padded_width//4:(padded_width*3//4)] = img
    return img_with_padding


def apply_ifft(img: np.ndarray) -> np.ndarray:
    ifft: np.ndarray = np.fft.ifft(np.fft.ifftshift(img, axes=1), axis=1)
    ifft = ifft.flatten()
    ifft /= np.max(ifft)
    return ifft


def make_iq(img: np.ndarray, outfile: str) -> None:
    iq: np.ndarray = np.zeros(2 * img.size, dtype=np.float32)
    iq[0::2] = np.real(img)
    iq[1::2] = np.imag(img)
    with open(outfile, 'wb') as f:
        f.write(iq.tobytes())


def main(input_image: str, samplerate: int = 192000, linetime: float = 0.01, output: str = 'out.iq') -> None:
    read: np.ndarray = imageio.v3.imread(input_image)
    img = np.copy(read)[::-1, ::-1, :]

    img = rgba_to_luma(img)
    img = repeat_lines(img, samplerate, linetime)
    img = image_padding(img)
    img = apply_ifft(img)

    make_iq(img, output)


if __name__ == '__main__':
    main('lain.png', linetime=0.01, samplerate=48000)
