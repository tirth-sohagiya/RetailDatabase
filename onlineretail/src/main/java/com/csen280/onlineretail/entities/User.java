package com.csen280.onlineretail.entities;

import com.csen280.onlineretail.enums.UserRole;

import jakarta.persistence.*;
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

    private String login_id;

    private String phone;

    private UserRole userRole;
    //private byte[] img;

}
