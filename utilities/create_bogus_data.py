from faker import Factory

fake = Factory.create()
print fake.paragraphs(nb=10)

