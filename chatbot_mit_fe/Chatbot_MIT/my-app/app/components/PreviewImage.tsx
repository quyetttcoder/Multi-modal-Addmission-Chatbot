interface PreviewImageProps {
    image: string;
    onClose: () => void;
}

export default function PreviewImage({
    image,
    onClose,
}: PreviewImageProps) {
    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
            onClick={onClose}
        >
            <img
                src={image}
                alt=""
                className="max-w-[90vw] max-h-[90vh] object-contain rounded-lg"
                onClick={(e) => e.stopPropagation()}
            />

            <button
                className="absolute top-4 right-4 text-white text-4xl cursor-pointer"
                onClick={onClose}
            >
                ×
            </button>
        </div>
    );
}