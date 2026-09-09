INSERT INTO
    USERS_LOGIN_SIS (
        user_login_sis_id,
        username,
        email,
        password,
        first_name,
        last_name
    )
VALUES
    (
        1,
        'admin',
        'admin@nbc.org.kh',
        '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
        'admin',
        'super'
    );

INSERT INTO
    SYSTEM (system_id, system_name)
VALUES
    (1, 'security');

INSERT INTO
    SYSTEM_LOGIN_SIS (system_login_sis_id, system_id, username, password)
VALUES
    (
        1,
        1,
        'security@nbc.com',
        '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
    );

INSERT INTO
    STATUS(status_id, status_name)
VALUES
    (1, 'PENDING');

INSERT INTO
    STATUS(status_id, status_name)
VALUES
    (2, 'SUCCESS');

INSERT INTO
    STATUS(status_id, status_name)
VALUES
    (3, 'FAIL');

INSERT INTO
    STATUS(status_id, status_name)
VALUES
    (4, 'ERROR');

INSERT INTO
    ENVIRONMENT(env_id, name)
VALUES
    (1, 'DEVELOPMENT');

INSERT INTO
    FLEXCUBE(
        flexcube_id,
        username,
        password,
        environment_id,
        flexcube_url,
        source,
        ubscomp,
        user_id,
        branch,
        module_id,
        service
    )
VALUES
    (
        1,
        'fcbs',
        '4abc7945016d442ff3ff0feb53b2bb0598081b6b86a672d977aa66390e422007',
        1,
        'http://172.16.17.229:7007/FCUBSDEService/FCUBSDEService?WSD',
        'FCAT',
        'FCUBS',
        'ITO1084',
        '001',
        'DE',
        'FCUBSDEService'
    );

INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(1, 'update status', 1, 'update-status');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(2, 'authentication for system', 1, 'authentication-for-systems');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(3, 'get flexcube date', 1, 'get-flexcube-date');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(4, 'get account balance', 1, 'get-account-balance');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(5, 'settlement cbs', 1, 'settlement-cbs');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(6, 'settlement iroha', 1, 'settlement-iroha');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(7, 'get status', 1, 'get-status');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(8, 'logout', 1, 'logout');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(9, 'create action', 1, 'create-action');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(10, 'edit action', 1, 'edit-action');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(11, 'list action', 1, 'list-action');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(12, 'action detail by id', 1, 'action-detail-by-id');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(13, 'create system', 1, 'create-system');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(14, 'create system user', 1, 'create-system-user');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(15, 'edit system user', 1, 'edit-system-user');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(16, 'edit system', 1, 'edit-system');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(17, 'list system', 1, 'list-system');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(18, 'system detail by id', 1, 'system-detail-by-id');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(19, 'create environment', 1, 'create-environment');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(20, 'edit environment', 1, 'edit-environment');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(21, 'list environment', 1, 'list-environment');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(22, 'environment detail by id', 1, 'environment-detail-by-id');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(23, 'create flexcube', 1, 'create-flexcube');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(24, 'edit flexcube', 1, 'edit-flexcube');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(25, 'list flexcube', 1, 'list-flexcube');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(26, 'flexcube detail by id', 1, 'flexcube-detail-by-id');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(27, 'create menu', 1, 'create-menu');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(28, 'edit menu', 1, 'edit-menu');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(29, 'get menu', 1, 'get-menu');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(30, 'list menu', 1, 'list-menu');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(31, 'create role', 1, 'create-role');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(32, 'edit role', 1, 'edit-role');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(33, 'list role', 1, 'list-role');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(34, 'get role', 1, 'get-role');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(35, 'create permission', 1, 'create-permission');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(36, 'edit permission', 1, 'edit-permission');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(37, 'create user', 1, 'create-user');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(38, 'create user role', 1, 'create-user-role');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(39, 'edit user role', 1, 'edit-user-role');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(40, 'list user', 1, 'list-user');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(41, 'user detail by id', 1, 'user-detail-by-id');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(42, 'change password', 1, 'change-password');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(43, 'reset password by email', 1, 'reset-password-by-email');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(44, 'user login', 1, 'user-login');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(45, 'user logout', 1, 'user-logout');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(46, 'user refresh token', 1, 'user-refresh-token');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(47, 'create iroha', 1, 'create-iroha');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(48, 'edit iroha', 1, 'edit-iroha');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(49, 'list iroha', 1, 'list-iroha');
INSERT INTO ACTION(ACTION_ID, NAME, STATUS, URL)VALUES(50, 'get iroha information', 1, 'get-iroha-information');