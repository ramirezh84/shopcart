PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT, 
		phone TEXT
		);
INSERT INTO "users" VALUES(1,'0cc175b9c0f1b6a831c399e269772661','abcd@example.com','Harsh','Shah','scaa','asa','as','asc','dasd','dfas','dsa');
INSERT INTO "users" VALUES(2,'eb908adcfe24f04e8ce967248c8aecef','ranohep@gmail.com','Enrique','Ramirez','809 Calliopsis St','NA','75068','Little Elm','TX','USA','4699707565');
CREATE TABLE products
		(productId INTEGER PRIMARY KEY,
		name TEXT,
		price REAL,
		description TEXT,
		image TEXT,
		stock INTEGER,
		categoryId INTEGER,
		FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
		);
INSERT INTO "products" VALUES(2,'Second',2.0,'Second Item','Kinkaku_Ji_by_Elizabeth_K_Joseph.jpg',2,1);
INSERT INTO "products" VALUES(3,'First',1.0,'First book.','Untitled_by_Troy_Jarrell.jpg',1,2);
INSERT INTO "products" VALUES(4,'T Shirt 1',1.0,'First T shirt','Kinkaku_Ji_by_Elizabeth_K_Joseph.jpg',1,1);
INSERT INTO "products" VALUES(5,'T Shirt 2',2.0,'Second T shirt','The_Sky_Is_The_Limit_by_Kaushik_Panchal.jpg',2,1);
INSERT INTO "products" VALUES(6,'T Shirt 3',3.0,'Third tshirt','Untitled_by_Troy_Jarrell.jpg',3,1);
INSERT INTO "products" VALUES(7,'T Shirt 4',4.0,'Fourth T shirt','Untitled_by_Aaron_Burden.jpg',4,1);
INSERT INTO "products" VALUES(8,'T Shirt 5',5.0,'FIfth Tshirt','The_Sky_Is_The_Limit_by_Kaushik_Panchal.jpg',5,1);
INSERT INTO "products" VALUES(9,'Book 1',1.0,'FIrst Book','Mountainous_View_by_Sven_Scheuermeier.jpg',1,2);
INSERT INTO "products" VALUES(10,'Book 2',2.0,'Second Book','The_Sky_Is_The_Limit_by_Kaushik_Panchal.jpg',2,2);
INSERT INTO "products" VALUES(11,'Book 3',3.0,'Third book.','Untitled_0026_by_Mike_Sinko.jpg',3,2);
INSERT INTO "products" VALUES(12,'Book 4',4.0,'Fourth book.','Untitled_7019_by_Mike_Sinko.jpg',4,2);
INSERT INTO "products" VALUES(13,'Book 5',5.0,'Fifth book.','Untitled_by_Troy_Jarrell.jpg',5,2);
INSERT INTO "products" VALUES(14,'Computer 1',1.0,'First computer','Untitled_by_Aaron_Burden.jpg',1,3);
INSERT INTO "products" VALUES(15,'Movie 1',1.0,'First mvoie','Yellow_Jacket_by_Manuel_Frei.png',1,4);
INSERT INTO "products" VALUES(16,'Jwelery 1',1.0,'First jwelery','Kinkaku_Ji_by_Elizabeth_K_Joseph.jpg',1,5);
INSERT INTO "products" VALUES(17,'Saree 1',1.0,'First saree','Mountainous_View_by_Sven_Scheuermeier.jpg',1,6);
CREATE TABLE kart
		(userId INTEGER,
		productId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(productId) REFERENCES products(productId)
		);
CREATE TABLE categories
		(categoryId INTEGER PRIMARY KEY,
		name TEXT
		);
INSERT INTO "categories" VALUES(1,'Men');
INSERT INTO "categories" VALUES(2,'Books');
INSERT INTO "categories" VALUES(3,'Computers and Accessories');
INSERT INTO "categories" VALUES(4,'Movies, Music and Video Games');
INSERT INTO "categories" VALUES(5,'Jwelery, Watches and Eyewear');
INSERT INTO "categories" VALUES(6,'Women');
COMMIT;
