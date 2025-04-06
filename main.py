# Replace:
Bot().run()

# With:
if __name__ == "__main__":
    bot = Bot()
    bot.start()  # Initialize
    bot.run()    # Keep running
