SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `alunos` (
  `id` int(11) NOT NULL,
  `nome` varchar(255) NOT NULL,
  `foto` varchar(255) NOT NULL,
  `turno` enum('manhã','tarde','integral') NOT NULL DEFAULT 'integral',
  `turma` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `configuracoes` (
  `id` int(11) NOT NULL,
  `nome_configuracao` varchar(255) NOT NULL,
  `valor` int(11) NOT NULL,
  `tipo` enum('minutos','horas') NOT NULL DEFAULT 'minutos',
  `descricao` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `configuracoes` (`id`, `nome_configuracao`, `valor`, `tipo`, `descricao`) VALUES
(1, 'tempo_espera', 1, 'minutos', 'Tempo de espera entre registros de entrada e saída');

CREATE TABLE `fotos_alunos` (
  `id_foto` int(11) NOT NULL,
  `id_aluno` int(11) NOT NULL,
  `foto_nome` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `registros_presenca` (
  `id` int(11) NOT NULL,
  `id_aluno` int(11) DEFAULT NULL,
  `tipo_registro` enum('entrada','saida') NOT NULL,
  `data_hora` timestamp NOT NULL DEFAULT current_timestamp(),
  `turma` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


ALTER TABLE `alunos`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `configuracoes`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `fotos_alunos`
  ADD PRIMARY KEY (`id_foto`),
  ADD KEY `id_aluno` (`id_aluno`);

ALTER TABLE `registros_presenca`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_aluno` (`id_aluno`);


ALTER TABLE `alunos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `configuracoes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

ALTER TABLE `fotos_alunos`
  MODIFY `id_foto` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `registros_presenca`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;


ALTER TABLE `fotos_alunos`
  ADD CONSTRAINT `fotos_alunos_ibfk_1` FOREIGN KEY (`id_aluno`) REFERENCES `alunos` (`id`) ON DELETE CASCADE;

ALTER TABLE `registros_presenca`
  ADD CONSTRAINT `registros_presenca_ibfk_1` FOREIGN KEY (`id_aluno`) REFERENCES `alunos` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
