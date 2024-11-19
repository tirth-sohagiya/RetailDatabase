-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart` (
  `cid` int NOT NULL AUTO_INCREMENT,
  `uid` int DEFAULT NULL,
  `pid` int NOT NULL,
  `quantity` int NOT NULL,
  `session_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`cid`),
  KEY `uid` (`uid`),
  KEY `pid` (`pid`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`),
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `product` (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (1,3,5,1,'35d44904-270a-4bb3-a4aa-d35299b386d6'),(2,3,3,1,'35d44904-270a-4bb3-a4aa-d35299b386d6'),(3,3,1,1,'35d44904-270a-4bb3-a4aa-d35299b386d6'),(4,3,4,1,NULL),(5,NULL,3,1,'35d44904-270a-4bb3-a4aa-d35299b386d6');
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `pid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(40) DEFAULT NULL,
  `price` varchar(8) DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `description` varchar(200) DEFAULT NULL,
  `stock` int DEFAULT NULL,
  `img_path` varchar(40) DEFAULT NULL,
  `popularity` int DEFAULT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES (1,'Laptop','1999.99','laptop','a cutting edge laptop for gaming',100,'laptop.jpg',1000),(2,'Acer Chromebook 315','139.00','laptop','The most accessible way to do the tasks you love',135,'acer315.jpg',2),(3,'MacBook Air 15','999.99','laptop','Lightweight and portable with all the features you expect from a Mac',200,'macbookair15.jpg',13241),(4,'MacBook Air 13','799.99','laptop','For those who value portability',27,'macbookair13.jpg',2534),(5,'MacBook Pro 15','1799.99','laptop','The most powerful macbook yet',199,'macbookpro15.jpg',78699),(6,'Lenovo Yoga 3 Pro','1199.99','laptop','Flexibility at a low cost',37,'yoga3pro.jpg',99),(7,'Ideapad 5','999.99','laptop','Where all the best ideas start',22,'ideapad5.jpg',27),(8,'Alienware X17 R2','2099.99','laptop','Unbeatable performance for serious gamers',67,'alienwarex17.jpg',99),(9,'Alienwware X15 R4','1899.99','laptop','For gamers on the go',23,'alienwarex15.jpg',97),(10,'Dell Inspiron 16','1399.99','laptop','Quality and portability',47,'dell16.jpg',800);
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `email` varchar(40) DEFAULT NULL,
  `name` varchar(40) DEFAULT NULL,
  `pass_hash` varchar(103) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'doug@gmail.com','doug','pbkdf2:sha256:1000000$ML7Dohb6Zz0Ctr8M$d6cfe5c9e011cce204f73a54caf1220215a577bd1bb63e9ed0d8415fcdf2f4ff'),(2,'bill@gmail.com','Bill','pbkdf2:sha256:1000000$3Hxitq8GA7wgrNS7$b4b7e6fbe3e1662dbe7e1d05bf5abf1f5c57a9ca78d03746dcd9ef2f7ac7cf4f'),(3,'tim@gmail.com','tim','pbkdf2:sha256:1000000$gdTwB4Y8oLLRg0pZ$caa8bf98993b24ed1481f9f8cdebd338f9a7ba74bad9e9787cdc39375d836472');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-18 18:04:38
