# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Kopiujemy tylko pliki pakietów, aby wykorzystać cache warstw Dockera
COPY package.json package-lock.json* ./

RUN npm install

# Kopiujemy resztę kodu
COPY . .

# Port, na którym domyślnie działa Vite
EXPOSE 5173

# Uruchomienie serwera deweloperskiego
CMD ["npm", "run", "dev"]