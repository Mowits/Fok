import os


def try_init_face(cfg: dict):
    if not cfg.get("face_enabled", False):
        return None
    try:
        import cv2
        import face_recognition
    except Exception:
        return None

    cam_index = int(cfg.get("face_camera_index", 0))
    faces_dir = cfg.get("faces_dir", "")
    if not faces_dir or not os.path.isdir(faces_dir):
        return None

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        return None

    known_encodings = []
    known_names = []
    for fname in os.listdir(faces_dir):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        path = os.path.join(faces_dir, fname)
        try:
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if enc:
                known_encodings.append(enc[0])
                known_names.append(os.path.splitext(fname)[0])
        except Exception:
            continue

    def identify_once():
        if not known_encodings:
            return None
        ret, frame = cap.read()
        if not ret:
            return None
        rgb = frame[:, :, ::-1]
        locs = face_recognition.face_locations(rgb, model="hog")
        encs = face_recognition.face_encodings(rgb, locs)
        for enc in encs:
            matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.5)
            if True in matches:
                idx = matches.index(True)
                return known_names[idx]
        return None

    def add_face(name: str):
        ret, frame = cap.read()
        if not ret:
            return False, "kamera okunamadi"
        rgb = frame[:, :, ::-1]
        locs = face_recognition.face_locations(rgb, model="hog")
        if not locs:
            return False, "yuz bulunamadi"
        encs = face_recognition.face_encodings(rgb, locs)
        if not encs:
            return False, "yuz kodu cikmadi"
        safe = "".join(ch for ch in name if ch.isalnum() or ch in ("_", "-")).strip()
        if not safe:
            return False, "gecersiz isim"
        path = os.path.join(faces_dir, f"{safe}.jpg")
        cv2.imwrite(path, frame)
        known_encodings.append(encs[0])
        known_names.append(safe)
        return True, safe

    return {"identify": identify_once, "add": add_face}


def try_init_emotion(cfg: dict):
    if not cfg.get("emotion_enabled", False):
        return None
    # Placeholder: gerçek duygu analizi için ayrı bir model gerekir.
    def detect_emotion():
        return None
    return detect_emotion
