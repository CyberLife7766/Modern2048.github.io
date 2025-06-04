// Define translations
const translations = {
    zh: {
        settingsTitle: "设置",
        darkModeLabel: "黑白模式",
        languageLabel: "语言",
        backButton: "返回游戏",
        scoreLabel: "分数",
        gameModeLabel: "游戏模式",
        boardSizeLabel: "棋盘尺寸"
    },
    en: {
        settingsTitle: "Settings",
        darkModeLabel: "Dark/Light Mode",
        languageLabel: "Language",
        backButton: "Back to Game",
        scoreLabel: "Score",
        gameModeLabel: "Game Mode",
        boardSizeLabel: "Board Size"
    },
    ja: {
        settingsTitle: "設定",
        darkModeLabel: "白黒モード",
        languageLabel: "言語",
        backButton: "ゲームに戻る",
        scoreLabel: "スコア",
        gameModeLabel: "ゲームモード",
        boardSizeLabel: "ボードサイズ"
    },
    de: {
        settingsTitle: "Einstellungen",
        darkModeLabel: "Dunkel/Hell Modus",
        languageLabel: "Sprache",
        backButton: "Zurück zum Spiel",
        scoreLabel: "Punktzahl",
        gameModeLabel: "Spielmodus",
        boardSizeLabel: "Brettgröße"
    },
    fr: {
        settingsTitle: "Paramètres",
        darkModeLabel: "Mode Sombre/Clair",
        languageLabel: "Langue",
        backButton: "Retour au Jeu",
        scoreLabel: "Score",
        gameModeLabel: "Mode de Jeu",
        boardSizeLabel: "Taille du Plateau"
    },
    ru: {
        settingsTitle: "Настройки",
        darkModeLabel: "Темный/Светлый Режим",
        languageLabel: "Язык",
        backButton: "Вернуться к Игре",
        scoreLabel: "Счет",
        gameModeLabel: "Режим Игры",
        boardSizeLabel: "Размер Доски"
    }
};

// Function to apply selected language to elements with data-key attribute
function applyLanguage(lang) {
    const currentTranslations = translations[lang];
    if (currentTranslations) {
        // Update elements in settings.html using data-key or specific IDs
        const settingsTitleElement = document.getElementById('settings-title');
        if (settingsTitleElement) { // Check if element exists (only on settings page)
            settingsTitleElement.textContent = currentTranslations.settingsTitle;
        }

        const darkModeLabelElement = document.querySelector('[data-key="darkModeLabel"]');
        if (darkModeLabelElement) {
            darkModeLabelElement.textContent = currentTranslations.darkModeLabel;
        }

        const languageLabelElement = document.querySelector('[data-key="languageLabel"]');
        if (languageLabelElement) {
            languageLabelElement.textContent = currentTranslations.languageLabel;
        }

        const backButtonElement = document.querySelector('[data-key="backButton"]');
        if (backButtonElement) {
            backButtonElement.textContent = currentTranslations.backButton;
        }

        const gameModeLabelElement = document.querySelector('[data-key="gameModeLabel"]');
        if (gameModeLabelElement) {
            gameModeLabelElement.textContent = currentTranslations.gameModeLabel;
        }

        const boardSizeLabelElement = document.querySelector('[data-key="boardSizeLabel"]');
        if (boardSizeLabelElement) {
            boardSizeLabelElement.textContent = currentTranslations.boardSizeLabel;
        }

        // Update elements in index.html (if they exist)
        const scoreLabelElement = document.getElementById('score-label');
        if (scoreLabelElement) {
            scoreLabelElement.textContent = currentTranslations.scoreLabel;
        }
    }
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    let currentLang = localStorage.getItem('language') || 'zh';
    // For settings page, set the select value
    const languageSelect = document.getElementById('language-select');
    if (languageSelect) {
        languageSelect.value = currentLang;
        languageSelect.addEventListener('change', (event) => {
            currentLang = event.target.value;
            localStorage.setItem('language', currentLang);
            applyLanguage(currentLang);
        });
    }
    applyLanguage(currentLang);
});
