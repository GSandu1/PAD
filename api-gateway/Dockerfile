FROM node:14

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./
RUN npm install

# Bundle app source code
COPY . .

# Expose port
EXPOSE 3000

# Start the app
CMD [ "node", "app.js" ]
