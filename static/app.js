// Global state
let currentUser = null
let authToken = null
let cart = []
let currentSection = "welcome"
let selectedSeats = []

// API Base URL
const API_BASE = "/api"

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  // Check for existing session
  const token = localStorage.getItem("authToken")
  const user = localStorage.getItem("currentUser")

  if (token && user) {
    authToken = token
    currentUser = JSON.parse(user)
    updateAuthUI()
  }

  // Load initial content
  showWelcome()

  // Setup form handlers
  setupFormHandlers()
})

// Authentication functions
function setupFormHandlers() {
  document.getElementById("loginForm").addEventListener("submit", handleLogin)
  document.getElementById("registerForm").addEventListener("submit", handleRegister)
}

async function handleLogin(e) {
  e.preventDefault()

  const email = document.getElementById("loginEmail").value
  const password = document.getElementById("loginPassword").value

  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        correo: email,
        contrasena: password,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      authToken = data.access_token
      currentUser = data.user

      localStorage.setItem("authToken", authToken)
      localStorage.setItem("currentUser", JSON.stringify(currentUser))

      updateAuthUI()
      showMovies()
      showNotification("¡Bienvenido!", "success")
    } else {
      const errorMessage = (data.detail && typeof data.detail === 'object' && data.detail.detail) ? data.detail.detail : (data.detail || "Error al iniciar sesión");
      showNotification(errorMessage, "error")
    }
  } catch (error) {
    showNotification("Error de conexión", "error")
  }
}

async function handleRegister(e) {
  e.preventDefault()

  const name = document.getElementById("registerName").value
  const age = Number.parseInt(document.getElementById("registerAge").value)
  const email = document.getElementById("registerEmail").value
  const password = document.getElementById("registerPassword").value

  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        nombre: name,
        edad: age,
        correo: email,
        contrasena: password,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      showNotification("Cuenta creada exitosamente. Ahora puedes iniciar sesión.", "success")
      showLogin()
    } else {
      showNotification(data.detail || "Error al crear cuenta", "error")
    }
  } catch (error) {
    showNotification("Error de conexión", "error")
  }
}

function logout() {
  authToken = null
  currentUser = null
  cart = []
  selectedSeats = []

  localStorage.removeItem("authToken")
  localStorage.removeItem("currentUser")

  updateAuthUI()
  showWelcome()
  showNotification("Sesión cerrada", "info")
}

function updateAuthUI() {
  const authButtons = document.getElementById("authButtons")
  const userMenu = document.getElementById("userMenu")
  const mainNav = document.getElementById("mainNav")
  const myTicketsLink = document.getElementById("myTicketsLink")
  const adminLink = document.getElementById("adminLink")

  if (currentUser) {
    authButtons.style.display = "none"
    userMenu.style.display = "flex"
    mainNav.style.display = "flex"
    document.getElementById("userName").textContent = currentUser.nombre

    if (currentUser.rol === "user") {
      myTicketsLink.style.display = "block"
      adminLink.style.display = "none"
    } else if (currentUser.rol === "admin") {
      myTicketsLink.style.display = "block"
      adminLink.style.display = "block"
      document.getElementById("addMovieBtn").style.display = "block"
      document.getElementById("addProductBtn").style.display = "block"
    }
  } else {
    authButtons.style.display = "flex"
    userMenu.style.display = "none"
    mainNav.style.display = "none"
    myTicketsLink.style.display = "none"
    adminLink.style.display = "none"
    document.getElementById("addMovieBtn").style.display = "none"
    document.getElementById("addProductBtn").style.display = "none"
  }
}

// Navigation functions
function showSection(sectionId) {
  // Hide all sections
  const sections = document.querySelectorAll(".welcome-section, .auth-section-content, .content-section")
  sections.forEach((section) => (section.style.display = "none"))

  // Show target section
  document.getElementById(sectionId).style.display = "block"
  currentSection = sectionId.replace("Section", "")
}

function showWelcome() {
  showSection("welcomeSection")
}

function showLogin() {
  showSection("loginSection")
}

function showRegister() {
  showSection("registerSection")
}

async function showMovies() {
  showSection("moviesSection")
  await loadMovies()
}

async function showProducts() {
  showSection("productsSection")
  await loadProducts()
}

async function showMyTickets() {
  if (!currentUser) {
    showLogin()
    return
  }
  showSection("ticketsSection")
  await loadUserTickets()
}

function showAdminPanel() {
  if (!currentUser || currentUser.rol !== "admin") {
    showNotification("Acceso denegado", "error")
    return
  }
  showSection("adminSection")
  showAdminTab("movies")
}

// Movies functions
async function loadMovies() {
  const grid = document.getElementById("moviesGrid")
  grid.innerHTML = '<div class="loading">Cargando películas...</div>'

  try {
    const response = await fetch(`${API_BASE}/movies/`)
    const movies = await response.json()

    grid.innerHTML = ""

    if (movies.length === 0) {
      grid.innerHTML = '<p class="text-center">No hay películas disponibles</p>'
      return
    }

    movies.forEach((movie) => {
      const movieCard = createMovieCard(movie)
      grid.appendChild(movieCard)
    })
  } catch (error) {
    grid.innerHTML = '<p class="text-center">Error al cargar películas</p>'
  }
}

function createMovieCard(movie) {
  const card = document.createElement("div")
  card.className = "movie-card fade-in"

  const posterUrl = movie.imagen_url || "/abstract-movie-poster.png"

  card.innerHTML = `
        <img src="${posterUrl}" alt="${movie.titulo}" class="movie-poster" 
             onerror="this.src='/abstract-movie-poster.png'">
        <div class="movie-info">
            <h3 class="movie-title">${movie.titulo}</h3>
            <div class="movie-details">
                <span>Director: ${movie.director}</span> • 
                <span>${movie.duracion} min</span> • 
                <span>${movie.clasificacion}</span> • 
                <span>${movie.genero}</span>
            </div>
            ${movie.sinopsis ? `<p class="movie-synopsis">${movie.sinopsis}</p>` : ""}
            <div class="movie-actions">
                <button class="btn btn-primary" onclick="showMovieDetails(${movie.id_pelicula})">
                    Ver Funciones
                </button>
                ${movie.trailer_url ? `<button class="btn btn-outline" onclick="playTrailer('${movie.trailer_url}')">Ver Trailer</button>` : ""}
            </div>
        </div>
    `

  return card
}

async function showMovieDetails(movieId) {
  try {
    // Load showtimes for this movie
    const response = await fetch(`${API_BASE}/theaters/showtimes?movie_id=${movieId}`)
    const showtimes = await response.json()

    const modalBody = document.getElementById("modalBody")
    modalBody.innerHTML = `
            <div class="movie-showtimes">
                <h3>Funciones Disponibles</h3>
                ${
                  showtimes.length === 0
                    ? "<p>No hay funciones disponibles para esta película</p>"
                    : showtimes
                        .map(
                          (showtime) => `
                        <div class="showtime-card">
                            <div class="showtime-info">
                                <strong>${new Date(showtime.horario).toLocaleString()}</strong>
                                <span>Sala: ${showtime.sala_nombre}</span>
                                <span>Asientos disponibles: ${showtime.asientos_disponibles}</span>
                                <span class="price">${showtime.precio}</span>
                            </div>
                            <button class="btn btn-primary" onclick="selectShowtime(${showtime.id_funcion})">
                                Seleccionar
                            </button>
                        </div>
                    `,
                        )
                        .join("")
                }
            </div>
        `

    document.getElementById("modal").style.display = "flex"
  } catch (error) {
    showNotification("Error al cargar funciones", "error")
  }
}

// Products functions
async function loadProducts(category = "all") {
  const grid = document.getElementById("productsGrid")
  grid.innerHTML = '<div class="loading">Cargando productos...</div>'

  try {
    const url = category === "all" ? `${API_BASE}/products/` : `${API_BASE}/products/?categoria=${category}`

    const response = await fetch(url)
    const products = await response.json()

    grid.innerHTML = ""

    if (products.length === 0) {
      grid.innerHTML = '<p class="text-center">No hay productos disponibles</p>'
      return
    }

    products.forEach((product) => {
      const productCard = createProductCard(product)
      grid.appendChild(productCard)
    })
  } catch (error) {
    grid.innerHTML = '<p class="text-center">Error al cargar productos</p>'
  }
}

function createProductCard(product) {
  const card = document.createElement("div")
  card.className = "product-card fade-in"

  const imageUrl = product.imagen_url || "/generic-food-product.png"

  card.innerHTML = `
        <img src="${imageUrl}" alt="${product.nombre}" class="product-image"
             onerror="this.src='/generic-food-product.png'">
        <div class="product-info">
            <h3 class="product-name">${product.nombre}</h3>
            ${product.descripcion ? `<p class="product-description">${product.descripcion}</p>` : ""}
            <div class="product-price">${product.precio}</div>
            <div class="product-stock">Stock: ${product.stock}</div>
            <button class="btn btn-primary btn-full" 
                    onclick="addToCart('product', ${product.id_producto}, '${product.nombre}', ${product.precio})"
                    ${product.stock === 0 ? "disabled" : ""}>
                ${product.stock === 0 ? "Agotado" : "Agregar al Carrito"}
            </button>
        </div>
    `

  return card
}

function filterProducts(category) {
  // Update active button
  document.querySelectorAll(".category-btn").forEach((btn) => btn.classList.remove("active"))
  event.target.classList.add("active")

  loadProducts(category)
}

// Cart functions
function addToCart(type, id, name, price, extra = {}) {
  const existingItem = cart.find((item) => item.type === type && item.id === id)

  if (existingItem) {
    existingItem.quantity += 1
  } else {
    cart.push({
      type,
      id,
      name,
      price,
      quantity: 1,
      ...extra,
    })
  }

  updateCartUI()
  showNotification(`${name} agregado al carrito`, "success")
}

function removeFromCart(index) {
  cart.splice(index, 1)
  updateCartUI()
}

function updateCartUI() {
  const cartItems = document.getElementById("cartItems")
  const cartTotal = document.getElementById("cartTotal")
  const cartCount = document.getElementById("cartCount")
  const cartToggle = document.getElementById("cartToggle")

  if (cart.length === 0) {
    cartItems.innerHTML = '<p class="text-center">El carrito está vacío</p>'
    cartToggle.style.display = "none"
  } else {
    cartToggle.style.display = "block"
    cartItems.innerHTML = cart
      .map(
        (item, index) => `
            <div class="cart-item">
                <div>
                    <strong>${item.name}</strong>
                    <div>${item.price} x ${item.quantity}</div>
                </div>
                <button class="btn btn-outline" onclick="removeFromCart(${index})">×</button>
            </div>
        `,
      )
      .join("")
  }

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
  cartTotal.textContent = total.toFixed(2)
  cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0)
}

function toggleCart() {
  const cartElement = document.getElementById("cart")
  cartElement.classList.toggle("open")
}

async function checkout() {
  if (!currentUser) {
    showLogin()
    return
  }

  if (cart.length === 0) {
    showNotification("El carrito está vacío", "error")
    return
  }

  try {
    const items = cart.map((item) => ({
      type: item.type,
      [`id_${item.type === "ticket" ? "funcion" : "producto"}`]: item.id,
      ...(item.type === "ticket" ? { asiento: item.seat } : { cantidad: item.quantity }),
    }))

    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)

    const response = await fetch(`${API_BASE}/tickets/purchase`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        id_usuario: currentUser.id_usuario,
        items,
        total,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      cart = []
      updateCartUI()
      toggleCart()
      showNotification("¡Compra realizada exitosamente!", "success")

      // Show purchase details
      showPurchaseDetails(data)
    } else {
      showNotification(data.detail || "Error al procesar la compra", "error")
    }
  } catch (error) {
    showNotification("Error de conexión", "error")
  }
}

// Utility functions
function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.textContent = message

  // Style the notification
  Object.assign(notification.style, {
    position: "fixed",
    top: "100px",
    right: "20px",
    padding: "1rem 1.5rem",
    borderRadius: "var(--radius)",
    color: "white",
    fontWeight: "500",
    zIndex: "1003",
    transform: "translateX(100%)",
    transition: "transform 0.3s ease",
  })

  // Set background color based on type
  const colors = {
    success: "#22c55e",
    error: "#ef4444",
    info: "#3b82f6",
    warning: "#f59e0b",
  }
  notification.style.backgroundColor = colors[type] || colors.info

  document.body.appendChild(notification)

  // Animate in
  setTimeout(() => {
    notification.style.transform = "translateX(0)"
  }, 100)

  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.transform = "translateX(100%)"
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 300)
  }, 3000)
}

function closeModal() {
  document.getElementById("modal").style.display = "none"
}

// Admin functions
function showAdminTab(tab) {
  // Update active tab
  document.querySelectorAll(".tab-btn").forEach((btn) => btn.classList.remove("active"))
  event.target.classList.add("active")

  const content = document.getElementById("adminContent")

  switch (tab) {
    case "movies":
      loadAdminMovies()
      break
    case "theaters":
      loadAdminTheaters()
      break
    case "showtimes":
      loadAdminShowtimes()
      break
    case "products":
      loadAdminProducts()
      break
    case "users":
      loadAdminUsers()
      break
    case "reports":
      loadAdminReports()
      break
  }
}

async function loadAdminMovies() {
  const content = document.getElementById("adminContent")
  content.innerHTML = '<div class="loading">Cargando...</div>'

  try {
    const response = await fetch(`${API_BASE}/movies/`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const movies = await response.json()

    content.innerHTML = `
            <div class="admin-section">
                <div class="section-header">
                    <h3>Gestión de Películas</h3>
                    <button class="btn btn-primary" onclick="showAddMovieForm()">Agregar Película</button>
                </div>
                <div class="admin-table">
                    ${movies
                      .map(
                        (movie) => `
                        <div class="admin-row">
                            <div class="admin-cell">
                                <strong>${movie.titulo}</strong>
                                <div>${movie.director} • ${movie.duracion} min • ${movie.genero}</div>
                            </div>
                            <div class="admin-actions">
                                <button class="btn btn-outline" onclick="editMovie(${movie.id_pelicula})">Editar</button>
                                <button class="btn btn-outline" onclick="deleteMovie(${movie.id_pelicula})">Eliminar</button>
                            </div>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
            </div>
        `
  } catch (error) {
    content.innerHTML = "<p>Error al cargar películas</p>"
  }
}

async function loadAdminTheaters() {
  const content = document.getElementById("adminContent")
  content.innerHTML = '<div class="loading">Cargando...</div>'

  try {
    const response = await fetch(`${API_BASE}/theaters/`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const theaters = await response.json()

    content.innerHTML = `
            <div class="admin-section">
                <div class="section-header">
                    <h3>Gestión de Salas</h3>
                    <button class="btn btn-primary" onclick="showAddTheaterForm()">Agregar Sala</button>
                </div>
                <div class="admin-table">
                    ${theaters
                      .map(
                        (theater) => `
                        <div class="admin-row">
                            <div class="admin-cell">
                                <strong>${theater.nombre}</strong>
                                <div>Capacidad: ${theater.capacidad} asientos</div>
                            </div>
                            <div class="admin-actions">
                                <button class="btn btn-outline" onclick="editTheater(${theater.id_sala})">Editar</button>
                                <button class="btn btn-outline" onclick="deleteTheater(${theater.id_sala})">Eliminar</button>
                            </div>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
            </div>
        `
  } catch (error) {
    content.innerHTML = "<p>Error al cargar salas</p>"
  }
}

async function loadAdminShowtimes() {
  const content = document.getElementById("adminContent")
  content.innerHTML = '<div class="loading">Cargando...</div>'

  try {
    const response = await fetch(`${API_BASE}/theaters/showtimes`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const showtimes = await response.json()

    content.innerHTML = `
            <div class="admin-section">
                <div class="section-header">
                    <h3>Gestión de Funciones</h3>
                    <button class="btn btn-primary" onclick="showAddShowtimeForm()">Agregar Función</button>
                </div>
                <div class="admin-table">
                    ${showtimes
                      .map(
                        (showtime) => `
                        <div class="admin-row">
                            <div class="admin-cell">
                                <strong>${showtime.pelicula_titulo}</strong>
                                <div>${new Date(showtime.horario).toLocaleString()} - Sala: ${showtime.sala_nombre}</div>
                                <div>Precio: ${showtime.precio} - Disponibles: ${showtime.asientos_disponibles}</div>
                            </div>
                            <div class="admin-actions">
                                <button class="btn btn-outline" onclick="editShowtime(${showtime.id_funcion})">Editar</button>
                                <button class="btn btn-outline" onclick="deleteShowtime(${showtime.id_funcion})">Eliminar</button>
                            </div>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
            </div>
        `
  } catch (error) {
    content.innerHTML = "<p>Error al cargar funciones</p>"
  }
}

async function loadAdminProducts() {
  const content = document.getElementById("adminContent")
  content.innerHTML = '<div class="loading">Cargando...</div>'

  try {
    const response = await fetch(`${API_BASE}/products/`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const products = await response.json()

    content.innerHTML = `
            <div class="admin-section">
                <div class="section-header">
                    <h3>Gestión de Productos</h3>
                    <button class="btn btn-primary" onclick="showAddProductForm()">Agregar Producto</button>
                </div>
                <div class="admin-table">
                    ${products
                      .map(
                        (product) => `
                        <div class="admin-row">
                            <div class="admin-cell">
                                <strong>${product.nombre}</strong>
                                <div>${product.categoria} - ${product.precio} - Stock: ${product.stock}</div>
                            </div>
                            <div class="admin-actions">
                                <button class="btn btn-outline" onclick="editProduct(${product.id_producto})">Editar</button>
                                <button class="btn btn-outline" onclick="deleteProduct(${product.id_producto})">Eliminar</button>
                            </div>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
            </div>
        `
  } catch (error) {
    content.innerHTML = "<p>Error al cargar productos</p>"
  }
}

async function loadAdminUsers() {
  const content = document.getElementById("adminContent")
  content.innerHTML = '<div class="loading">Cargando...</div>'

  try {
    const response = await fetch(`${API_BASE}/auth/users`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const users = await response.json()

    content.innerHTML = `
            <div class="admin-section">
                <div class="section-header">
                    <h3>Gestión de Usuarios</h3>
                </div>
                <div class="admin-table">
                    ${users
                      .map(
                        (user) => `
                        <div class="admin-row">
                            <div class="admin-cell">
                                <strong>${user.nombre}</strong>
                                <div>${user.correo} - ${user.rol} - Edad: ${user.edad}</div>
                            </div>
                            <div class="admin-actions">
                                <button class="btn btn-outline" onclick="toggleUserRole(${user.id_usuario}, '${user.rol}')">
                                    ${user.rol === "admin" ? "Hacer Usuario" : "Hacer Admin"}
                                </button>
                            </div>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
            </div>
        `
  } catch (error) {
    content.innerHTML = "<p>Error al cargar usuarios</p>"
  }
}

async function loadAdminReports() {
  const content = document.getElementById("adminContent")
  content.innerHTML = '<div class="loading">Cargando...</div>'

  try {
    const response = await fetch(`${API_BASE}/tickets/reports`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const reports = await response.json()

    content.innerHTML = `
            <div class="admin-section">
                <h3>Reportes de Ventas</h3>
                <div class="reports-grid">
                    <div class="report-card">
                        <h4>Ventas Totales</h4>
                        <div class="report-value">${reports.total_sales || 0}</div>
                    </div>
                    <div class="report-card">
                        <h4>Boletos Vendidos</h4>
                        <div class="report-value">${reports.tickets_sold || 0}</div>
                    </div>
                    <div class="report-card">
                        <h4>Productos Vendidos</h4>
                        <div class="report-value">${reports.products_sold || 0}</div>
                    </div>
                    <div class="report-card">
                        <h4>Usuarios Registrados</h4>
                        <div class="report-value">${reports.total_users || 0}</div>
                    </div>
                </div>
                <div class="popular-movies">
                    <h4>Películas Más Populares</h4>
                    ${(reports.popular_movies || [])
                      .map(
                        (movie) => `
                        <div class="popular-item">
                            <span>${movie.titulo}</span>
                            <span>${movie.boletos_vendidos} boletos</span>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
            </div>
        `
  } catch (error) {
    content.innerHTML = "<p>Error al cargar reportes</p>"
  }
}

// Seat selection functionality
async function selectShowtime(showtimeId) {
  try {
    const response = await fetch(`${API_BASE}/theaters/showtimes/${showtimeId}/seats`)
    const seats = await response.json()

    const modalBody = document.getElementById("modalBody")
    modalBody.innerHTML = `
            <div class="seat-selection">
                <h3>Seleccionar Asientos</h3>
                <div class="screen">PANTALLA</div>
                <div class="seats-grid">
                    ${seats
                      .map(
                        (seat) => `
                        <div class="seat ${seat.ocupado ? "occupied" : "available"}" 
                             data-seat="${seat.numero}"
                             onclick="${seat.ocupado ? "" : `toggleSeat('${seat.numero}')`}">
                            ${seat.numero}
                        </div>
                    `,
                      )
                      .join("")}
                </div>
                <div class="seat-legend">
                    <div class="legend-item">
                        <div class="seat available"></div>
                        <span>Disponible</span>
                    </div>
                    <div class="legend-item">
                        <div class="seat selected"></div>
                        <span>Seleccionado</span>
                    </div>
                    <div class="legend-item">
                        <div class="seat occupied"></div>
                        <span>Ocupado</span>
                    </div>
                </div>
                <div class="seat-actions">
                    <div id="selectedSeats">Asientos seleccionados: Ninguno</div>
                    <button class="btn btn-primary" onclick="confirmSeatSelection(${showtimeId})" disabled id="confirmSeatsBtn">
                        Confirmar Selección
                    </button>
                </div>
            </div>
        `
  } catch (error) {
    showNotification("Error al cargar asientos", "error")
  }
}

function toggleSeat(seatNumber) {
  const seatElement = document.querySelector(`[data-seat="${seatNumber}"]`)
  const index = selectedSeats.indexOf(seatNumber)

  if (index > -1) {
    selectedSeats.splice(index, 1)
    seatElement.classList.remove("selected")
  } else {
    selectedSeats.push(seatNumber)
    seatElement.classList.add("selected")
  }

  updateSeatSelection()
}

function updateSeatSelection() {
  const selectedSeatsDiv = document.getElementById("selectedSeats")
  const confirmBtn = document.getElementById("confirmSeatsBtn")

  if (selectedSeats.length === 0) {
    selectedSeatsDiv.textContent = "Asientos seleccionados: Ninguno"
    confirmBtn.disabled = true
  } else {
    selectedSeatsDiv.textContent = `Asientos seleccionados: ${selectedSeats.join(", ")}`
    confirmBtn.disabled = false
  }
}

async function confirmSeatSelection(showtimeId) {
  if (selectedSeats.length === 0) return

  try {
    // Get showtime details for pricing
    const response = await fetch(`${API_BASE}/theaters/showtimes/${showtimeId}`)
    const showtime = await response.json()

    // Add tickets to cart
    selectedSeats.forEach((seat) => {
      addToCart("ticket", showtimeId, `${showtime.pelicula_titulo} - ${seat}`, showtime.precio, {
        seat: seat,
        showtime: showtime.horario,
        theater: showtime.sala_nombre,
      })
    })

    selectedSeats = []
    closeModal()
    showNotification("Boletos agregados al carrito", "success")
  } catch (error) {
    showNotification("Error al agregar boletos", "error")
  }
}

// Form functions for admin operations
function showAddMovieForm() {
  const modalBody = document.getElementById("modalBody")
  modalBody.innerHTML = `
        <div class="admin-form">
            <h3>Agregar Película</h3>
            <form id="addMovieForm">
                <div class="form-group">
                    <label for="movieTitle">Título</label>
                    <input type="text" id="movieTitle" required>
                </div>
                <div class="form-group">
                    <label for="movieDirector">Director</label>
                    <input type="text" id="movieDirector" required>
                </div>
                <div class="form-group">
                    <label for="movieDuration">Duración (minutos)</label>
                    <input type="number" id="movieDuration" required>
                </div>
                <div class="form-group">
                    <label for="movieGenre">Género</label>
                    <input type="text" id="movieGenre" required>
                </div>
                <div class="form-group">
                    <label for="movieClassification">Clasificación</label>
                    <select id="movieClassification" required>
                        <option value="G">G - Público General</option>
                        <option value="PG">PG - Se Sugiere Supervisión</option>
                        <option value="PG-13">PG-13 - Mayores de 13</option>
                        <option value="R">R - Restringida</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="movieSynopsis">Sinopsis</label>
                    <textarea id="movieSynopsis" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label for="movieImage">Imagen/Poster</label>
                    <input type="file" id="movieImage" accept="image/*">
                </div>
                <div class="form-group">
                    <label for="movieTrailer">URL del Trailer</label>
                    <input type="url" id="movieTrailer">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-outline" onclick="closeModal()">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Agregar Película</button>
                </div>
            </form>
        </div>
    `

  document.getElementById("addMovieForm").addEventListener("submit", handleAddMovie)
  document.getElementById("modal").style.display = "flex"
}

async function handleAddMovie(e) {
  e.preventDefault()

  const formData = new FormData()
  formData.append("titulo", document.getElementById("movieTitle").value)
  formData.append("director", document.getElementById("movieDirector").value)
  formData.append("duracion", document.getElementById("movieDuration").value)
  formData.append("genero", document.getElementById("movieGenre").value)
  formData.append("clasificacion", document.getElementById("movieClassification").value)
  formData.append("sinopsis", document.getElementById("movieSynopsis").value)
  formData.append("trailer_url", document.getElementById("movieTrailer").value)

  const imageFile = document.getElementById("movieImage").files[0]
  if (imageFile) {
    formData.append("imagen", imageFile)
  }

  try {
    const response = await fetch(`${API_BASE}/movies/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
      body: formData,
    })

    if (response.ok) {
      closeModal()
      showNotification("Película agregada exitosamente", "success")
      loadAdminMovies()
    } else {
      const error = await response.json()
      showNotification(error.detail || "Error al agregar película", "error")
    }
  } catch (error) {
    showNotification("Error de conexión", "error")
  }
}

function showAddProductForm() {
  const modalBody = document.getElementById("modalBody")
  modalBody.innerHTML = `
        <div class="admin-form">
            <h3>Agregar Producto</h3>
            <form id="addProductForm">
                <div class="form-group">
                    <label for="productName">Nombre</label>
                    <input type="text" id="productName" required>
                </div>
                <div class="form-group">
                    <label for="productCategory">Categoría</label>
                    <select id="productCategory" required>
                        <option value="combo">Combo</option>
                        <option value="snack">Snack</option>
                        <option value="bebida">Bebida</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="productPrice">Precio</label>
                    <input type="number" id="productPrice" step="0.01" required>
                </div>
                <div class="form-group">
                    <label for="productStock">Stock</label>
                    <input type="number" id="productStock" required>
                </div>
                <div class="form-group">
                    <label for="productDescription">Descripción</label>
                    <textarea id="productDescription" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label for="productImage">Imagen</label>
                    <input type="file" id="productImage" accept="image/*">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-outline" onclick="closeModal()">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Agregar Producto</button>
                </div>
            </form>
        </div>
    `

  document.getElementById("addProductForm").addEventListener("submit", handleAddProduct)
  document.getElementById("modal").style.display = "flex"
}

async function handleAddProduct(e) {
  e.preventDefault()

  const formData = new FormData()
  formData.append("nombre", document.getElementById("productName").value)
  formData.append("categoria", document.getElementById("productCategory").value)
  formData.append("precio", document.getElementById("productPrice").value)
  formData.append("stock", document.getElementById("productStock").value)
  formData.append("descripcion", document.getElementById("productDescription").value)

  const imageFile = document.getElementById("productImage").files[0]
  if (imageFile) {
    formData.append("imagen", imageFile)
  }

  try {
    const response = await fetch(`${API_BASE}/products/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
      body: formData,
    })

    if (response.ok) {
      closeModal()
      showNotification("Producto agregado exitosamente", "success")
      loadAdminProducts()
    } else {
      const error = await response.json()
      showNotification(error.detail || "Error al agregar producto", "error")
    }
  } catch (error) {
    showNotification("Error de conexión", "error")
  }
}

// User tickets loading function
async function loadUserTickets() {
  const grid = document.getElementById("ticketsGrid")
  grid.innerHTML = '<div class="loading">Cargando boletos...</div>'

  try {
    const response = await fetch(`${API_BASE}/tickets/user/${currentUser.id_usuario}`, {
      headers: { Authorization: `Bearer ${authToken}` },
    })
    const tickets = await response.json()

    grid.innerHTML = ""

    if (tickets.length === 0) {
      grid.innerHTML = '<p class="text-center">No tienes boletos comprados</p>'
      return
    }

    tickets.forEach((ticket) => {
      const ticketCard = createTicketCard(ticket)
      grid.appendChild(ticketCard)
    })
  } catch (error) {
    grid.innerHTML = '<p class="text-center">Error al cargar boletos</p>'
  }
}

function createTicketCard(ticket) {
  const card = document.createElement("div")
  card.className = "ticket-card fade-in"

  const statusClass = ticket.estado === "activo" ? "active" : ticket.estado === "usado" ? "used" : "cancelled"

  card.innerHTML = `
        <div class="ticket-qr">🎫</div>
        <div class="ticket-info">
            <h3>${ticket.pelicula_titulo}</h3>
            <div class="ticket-details">
                <div>Función: ${new Date(ticket.horario).toLocaleString()}</div>
                <div>Sala: ${ticket.sala_nombre}</div>
                <div>Asiento: ${ticket.asiento}</div>
                <div>Precio: ${ticket.precio}</div>
            </div>
        </div>
        <div class="ticket-status ${statusClass}">
            ${ticket.estado.toUpperCase()}
        </div>
    `

  return card
}

// Trailer playback function
function playTrailer(trailerUrl) {
  const modalBody = document.getElementById("modalBody")
  modalBody.innerHTML = `
        <div class="trailer-player">
            <iframe width="800" height="450" 
                    src="${trailerUrl}" 
                    frameborder="0" 
                    allowfullscreen>
            </iframe>
        </div>
    `
  document.getElementById("modal").style.display = "flex"
}

// Purchase details display
function showPurchaseDetails(purchaseData) {
  const modalBody = document.getElementById("modalBody")
  modalBody.innerHTML = `
        <div class="purchase-success">
            <h3>¡Compra Exitosa!</h3>
            <div class="purchase-details">
                <p><strong>ID de Compra:</strong> ${purchaseData.id}</p>
                <p><strong>Total:</strong> ${purchaseData.total}</p>
                <p><strong>Fecha:</strong> ${new Date().toLocaleString()}</p>
            </div>
            <div class="purchase-items">
                <h4>Artículos Comprados:</h4>
                ${purchaseData.items
                  .map(
                    (item) => `
                    <div class="purchase-item">
                        ${item.name} - ${item.price}
                        ${item.seat ? ` - Asiento: ${item.seat}` : ` - Cantidad: ${item.quantity}`}
                    </div>
                `,
                  )
                  .join("")}
            </div>
            <button class="btn btn-primary" onclick="closeModal()">Cerrar</button>
        </div>
    `
  document.getElementById("modal").style.display = "flex"
}

// Initialize cart toggle visibility
document.addEventListener("DOMContentLoaded", () => {
  updateCartUI()
})
