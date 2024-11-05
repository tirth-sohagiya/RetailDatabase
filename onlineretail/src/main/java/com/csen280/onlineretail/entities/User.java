package com.csen280.onlineretail.entities;

import com.csen280.onlineretail.enums.UserRole;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import lombok.Data;


@Entity
@Data
@Table(name = "user")

public class User {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    private String email;

    private UserRole userRole;
    //private byte[] img;

}
