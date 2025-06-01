workspace {
    name "Facebook"
    !identifiers hierarchical

    model {
        user = person "Пользователь" {
            description "Пользователь социальной сети"
        }
        
        admin = person "Администратор" {
            description "Администратор социальной сети, управляющий контентом и пользователями"
        }
        
        socialNetwork = softwareSystem "Социальная сеть" {
            description "Платформа для общения, публикаций на стене и обмена личными сообщениями"

            apiService = container "API Service" {
                technology "Python / FastAPI"
                description "Backend-сервис, реализующий бизнес-логику: регистрация, поиск, публикации и управление системой"
            }
            
            database = container "Database" {
                technology "PostgreSQL"
                description "База данных для хранения информации о пользователях, публикациях и сообщениях"
            }
            
            chatService = container "Chat Service" {
                technology "Node.js / WebSocket"
                description "Сервис для обработки личных сообщений между пользователями"
            }

            user -> apiService "Взаимодействует с системой через API" "REST/JSON"
            admin -> apiService "Управляет системой через API" "REST/JSON"
            
            apiService -> database "SQL-запросы" "POSTGRESQL"
            apiService -> chatService "Пересылает запросы на отправку сообщений" "REST/JSON"
            chatService -> database "Сохраняет и извлекает сообщения" "SQL"
        }
    }

    views {
        themes default

        systemContext socialNetwork {
            include *
            autolayout lr
        }

        container socialNetwork {
            include *
            autolayout lr
        }

        dynamic socialNetwork "create_user" "Создание нового пользователя" {
            autoLayout lr
            user -> socialNetwork.apiService "POST /api/v1/user/create"
            socialNetwork.apiService -> socialNetwork.database "Сохраняет данные пользователя"
        }

        dynamic socialNetwork "search_user_by_login" "Поиск пользователя по логину" {
            autoLayout lr
            user -> socialNetwork.apiService "GET /api/v1/user/search/login"
            socialNetwork.apiService -> socialNetwork.database "Запрос данных пользователя"
        }

        dynamic socialNetwork "search_user_by_name" "Поиск пользователя по имени и фамилии" {
            autoLayout lr
            user -> socialNetwork.apiService "POST /api/v1/user/search"
            socialNetwork.apiService -> socialNetwork.database "Получает данные пользователя"
        }

        dynamic socialNetwork "post_wall" "Добавление записи на стену" {
            autoLayout lr
            user -> socialNetwork.apiService "POST /api/v1/wall/post"
            socialNetwork.apiService -> socialNetwork.database "Сохраняет запись на стене"
        }

        dynamic socialNetwork "get_wall" "Загрузка стены пользователя" {
            autoLayout lr
            user -> socialNetwork.apiService "GET /api/v1/wall"
            socialNetwork.apiService -> socialNetwork.database "Извлекает записи со стены"
        }

        dynamic socialNetwork "send_message" "Отправка личного сообщения" {
            autoLayout lr
            user -> socialNetwork.apiService "POST /api/v1/message/send"
            socialNetwork.apiService -> socialNetwork.chatService "Перенаправляет сообщение"
            socialNetwork.chatService -> socialNetwork.database "Сохраняет сообщение"
        }

        dynamic socialNetwork "get_messages" "Получение списка сообщений" {
            autoLayout lr
            user -> socialNetwork.apiService "GET /api/v1/message"
            socialNetwork.apiService -> socialNetwork.chatService "Запрос личных сообщений"
            socialNetwork.chatService -> socialNetwork.database "Извлекает сообщения"
        }
    }
}