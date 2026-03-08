FROM node:22-alpine

WORKDIR /app

ENV NODE_ENV=development

COPY package.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
