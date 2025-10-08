# 🎓 Attendance Management System

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-red.svg)
![Flask](https://img.shields.io/badge/Flask-API-black.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)

**An intelligent, face recognition-based attendance management system built with Python, OpenCV, and modern web technologies.**

[Features](#-key-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-system-architecture) • [API](#-api-documentation) • [Contributing](#-contributing)

---

## 📺 Demo Video

> See the Attendance Management System in action on [YouTube](https://youtu.be/9BWvfd2Gnkk)

<a href="https://youtu.be/9BWvfd2Gnkk" target="_blank">
  <img src="https://img.youtube.com/vi/9BWvfd2Gnkk/0.jpg" alt="Watch Demo Video" width="480" />
</a>

---

</div>

---

## 📋 Table of Contents

- [About](#-about)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
  - [Training the Face Recognition Model](#1-training-the-face-recognition-model)
  - [Running Attendance Recognition](#2-running-attendance-recognition)
  - [Web Dashboard](#3-web-dashboard-streamlit)
  - [REST API](#4-rest-api-flask)
  - [Library Usage](#5-library-usage)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Documentation](#-api-documentation)
- [Workflow Details](#-workflow-details)
- [Troubleshooting](#-troubleshooting)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Security Considerations](#-security-considerations)
- [License](#-license)
- [Maintainers](#-maintainers)
- [Acknowledgements](#-acknowledgements)

---

## 🌟 About

The **Attendance Management System** is a comprehensive, AI-powered solution for automated attendance tracking using facial recognition technology. Built with Python and leveraging OpenCV's LBPH (Local Binary Patterns Histograms) face recognition algorithm, this system provides a touchless, efficient, and accurate method for managing attendance in educational institutions, offices, or any organization requiring reliable attendance tracking.

The system combines computer vision, machine learning, and modern web technologies to deliver:
- **Real-time face detection and recognition** using webcam/camera feeds
- **Automated attendance marking** with duplicate prevention
- **Web-based administrative dashboard** for attendance management
- **RESTful API** for third-party integrations
- **Email notifications** for absent students/employees
- **Export capabilities** (CSV, Excel) for reporting

---

## ✨ Key Features

### 🎯 Core Features
- ✅ **Face Recognition-Based Attendance**: Automated attendance marking using LBPH face recognition
- ✅ **Real-time Processing**: Live camera feed processing for instant attendance marking
- ✅ **Idempotent Operations**: Prevents duplicate attendance entries for the same person on the same day
- ✅ **Multi-person Recognition**: Detects and recognizes multiple faces simultaneously
- ✅ **Confidence Scoring**: Adjustable confidence threshold for recognition accuracy

### 📊 Administrative Features
- 📈 **Interactive Dashboard**: Streamlit-based web interface for attendance management
- 📧 **Email Notifications**: Automatic absent notifications via SMTP
- 📁 **Data Export**: Export attendance records in CSV and Excel formats
- 📅 **Date-based Filtering**: View and manage attendance by specific dates
- 🔍 **Student Roster Management**: View and manage student information

### 🔧 Technical Features
- 🗄️ **SQLite Database**: Lightweight, serverless database for attendance records
- 🌐 **RESTful API**: Flask-based API for programmatic access
- 🎨 **Modern UI**: Clean, responsive web interface
- 🔐 **Secure Configuration**: Environment-based configuration management
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring

---

## 🏗️ System Architecture

... *(rest of the README remains unchanged, except for the new demo video section above)* ...

---

**Attendance Management System** © 2025 | Made with Python 🐍

</div>
