document.addEventListener("DOMContentLoaded", () => {
    // === MATRIX RAIN CANVAS ===
    const canvas = document.getElementById('matrix-bg');
    const ctx = canvas.getContext('2d');
    
    // Set width and height
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレゲゼデベペオォコソトノホモヨョロゴゾドボポヴッン';
    const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const nums = '0123456789';
    const alphabet = katakana + latin + nums;

    const fontSize = 16;
    const columns = canvas.width / fontSize;
    const rainDrops = Array.from({ length: columns }).fill(canvas.height); // Start offscreen

    const drawMatrix = () => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#0F0';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < rainDrops.length; i++) {
            const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
            ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
            
            if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                rainDrops[i] = 0;
            }
            rainDrops[i]++;
        }
    };
    setInterval(drawMatrix, 35);
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    // ==========================

    const orb = document.getElementById("jarvis-orb");
    const statusText = document.getElementById("status-text");
    const chatHistory = document.getElementById("chat-history");
    const manualInput = document.getElementById("manual-input");
    const sendBtn = document.getElementById("send-btn");
    
    // Web Speech API Initialization
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'tr-TR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        recognition.onstart = () => {
            setOrbState('listening');
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            addMessage(transcript, 'user');
            sendToBackend(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('Ses tanıma hatası:', event.error);
            setOrbState('idle');
        };
        
        recognition.onend = () => {
            if (orb.classList.contains('listening')) {
                setOrbState('idle');
            }
        };
    } else {
        console.warn("Speech Recognition API desteklenmiyor.");
        statusText.innerText = "S_P_E_E_C_H_A_P_I_F_A_I_L";
    }

    const synth = window.speechSynthesis;

    const setOrbState = (state) => {
        orb.classList.remove('idle', 'listening', 'thinking', 'speaking');
        orb.classList.add(state);
        
        const stateTexts = {
            'idle': 'S_Y_S_R_E_A_D_Y',
            'listening': 'A_U_D_I_O_I_N_P_U_T',
            'thinking': 'P_R_O_C_E_S_S_I_N_G',
            'speaking': 'T_R_A_N_S_M_I_T_T_I_N_G'
        };
        statusText.innerText = stateTexts[state] || state.toUpperCase();
    };

    setOrbState('idle');

    orb.addEventListener("click", () => {
        if (!recognition) {
            typeEffect("HATA: Desteklenmeyen tarayıcı sürümü. Modül yüklenemedi.", 'error');
            return;
        }

        if (orb.classList.contains('listening')) {
            recognition.stop();
        } else {
            if (synth.speaking) synth.cancel();
            try {
                recognition.start();
            } catch (e) {
                console.error("Dinleme başlatılamadı:", e);
            }
        }
    });

    sendBtn.addEventListener("click", () => {
        const text = manualInput.value.trim();
        if (text) {
            addMessage(text, 'user');
            sendToBackend(text);
            manualInput.value = '';
        }
    });

    manualInput.addEventListener("keypress", (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });

    // Anında Ekleme Fonksiyonu
    const addMessage = (text, sender) => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("msg", sender);
        
        const promptSpan = document.createElement("span");
        promptSpan.classList.add("prompt");
        promptSpan.innerText = sender === 'user' ? "USER@SYS:~$" : "JARVIS@SYS:~$";

        const textSpan = document.createElement("span");
        textSpan.classList.add("text");
        textSpan.textContent = text;

        msgDiv.appendChild(promptSpan);
        msgDiv.appendChild(textSpan);

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    };

    // Hacker stili daktilo efekti
    const typeEffect = (text, senderType) => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("msg", senderType);
        
        const promptSpan = document.createElement("span");
        promptSpan.classList.add("prompt");
        promptSpan.innerText = senderType === 'error' ? "SYS_ERR:~$" : "JARVIS@SYS:~$";

        const textSpan = document.createElement("span");
        textSpan.classList.add("text");
        
        const cursor = document.createElement("span");
        cursor.classList.add("cursor");

        msgDiv.appendChild(promptSpan);
        msgDiv.appendChild(textSpan);
        msgDiv.appendChild(cursor);

        chatHistory.appendChild(msgDiv);

        let i = 0;
        let isTyping = true;
        
        const typeChar = () => {
            if (i < text.length) {
                textSpan.textContent += text.charAt(i);
                i++;
                chatHistory.scrollTop = chatHistory.scrollHeight;
                // Hacker typing speed: fast and mechanical (10-30 ms)
                setTimeout(typeChar, Math.random() * 20 + 10);
            } else {
                isTyping = false;
                cursor.style.display = 'none'; // hide cursor when done
            }
        };
        typeChar();
    };

    const speakText = (text) => {
        if (synth.speaking) synth.cancel(); 
        
        // Clean text for speech (Optional: Removing markdown symbols if any exist later)
        const cleanText = text.replace(/[*_~`]/g, '');

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'tr-TR';
        
        // Make it sound slightly robotic/faster
        utterance.pitch = 0.9;
        utterance.rate = 1.1;
        
        utterance.onstart = () => setOrbState('speaking');
        utterance.onend = () => setOrbState('idle');
        utterance.onerror = (e) => {
            console.error("Metin okuma hatası:", e);
            setOrbState('idle');
        };

        const voices = synth.getVoices();
        const trVoice = voices.find(voice => voice.lang.includes('tr'));
        if (trVoice) utterance.voice = trVoice;
        
        synth.speak(utterance);
    };

    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = () => {};
    }

    const sendToBackend = async (message) => {
        setOrbState('thinking');
        
        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            if (data.status === "success" || data.status === "action") {
                typeEffect(data.response, 'ai');
                speakText(data.response);
            } else {
                typeEffect("HATA_KODU: [" + data.message + "]", 'error');
                setOrbState('idle');
            }
            
        } catch (error) {
            console.error("API hatası:", error);
            typeEffect("KRİTİK HATA: Bağlantı reddedildi. Servis çevrimdışı.", 'error');
            setOrbState('idle');
        }
    };
});
