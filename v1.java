import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.*;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

public class v1 extends JFrame {

    private static final int SERVER_PORT = 12345;
    private static final String SERVER_IP = "127.0.0.1";

    private Socket socket;
    private DataOutputStream dos;
    private JTextField filePathField;

    private final String defaultFilePath = "C:\\Users\\hp\\Documents\\Python\\Face Recognition\\Attendance.csv";
    private DefaultTableModel tableModel;
    private JTabbedPane tabbedPane;
    private JPanel attendancePanel;
    private JPanel tablePanel;
    private JTable table;

    public v1() {
        setTitle("Attendance Control");

        // Control panel
        JPanel controlPanel = new JPanel();
        controlPanel.setBackground(Color.decode("#E3F2FD"));
        controlPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        JButton startButton = new JButton("Start Webcam");
        startButton.addActionListener(e -> sendCommand("1"));
        controlPanel.add(startButton);

        // Main tabbed pane
        tabbedPane = new JTabbedPane();
        tabbedPane.setBackground(Color.WHITE);

        // Attendance tab
        attendancePanel = new JPanel(new BorderLayout());
        attendancePanel.setBackground(Color.WHITE);

        // Refresh button panel
        JPanel refreshPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        refreshPanel.setBackground(Color.WHITE);
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> refreshTable(defaultFilePath));
        refreshPanel.add(refreshButton);

        // Clear button
        JButton clearButton = new JButton("Clear");
        clearButton.addActionListener(e -> clearAttendanceFile(defaultFilePath));
        refreshPanel.add(clearButton);

        attendancePanel.add(refreshPanel, BorderLayout.NORTH);

        // Table panel
        tablePanel = new JPanel(new BorderLayout());
        tablePanel.setBackground(Color.WHITE);
        attendancePanel.add(tablePanel, BorderLayout.CENTER);

        // Initially read CSV and create table
        readCSV(defaultFilePath);

        tabbedPane.addTab("Attendance", null, attendancePanel, "View Attendance");

        // Save attendance tab
        JPanel saveAttendancePanel = new JPanel(new BorderLayout());
        saveAttendancePanel.setBackground(Color.WHITE);
        JTextField saveFileNameField = new JTextField(20);
        JButton saveButton = new JButton("Save Attendance");
        saveButton.addActionListener(e -> saveAttendance(saveFileNameField.getText()));
        JPanel savePanel = new JPanel();
        savePanel.setBackground(Color.WHITE);
        savePanel.add(new JLabel("Enter file name: "));
        savePanel.add(saveFileNameField);
        savePanel.add(saveButton);
        saveAttendancePanel.add(savePanel, BorderLayout.NORTH);
        tabbedPane.addTab("Save Attendance", null, saveAttendancePanel, "Save Attendance");

        // Attendance analysis tab
        JPanel analyzeAttendancePanel = new JPanel();
        analyzeAttendancePanel.setLayout(new BorderLayout());
        analyzeAttendancePanel.setBackground(Color.WHITE);
        JButton analyzeButton = new JButton("Analyze");
        JTextArea analysisTextArea = new JTextArea();
        JScrollPane analysisScrollPane = new JScrollPane(analysisTextArea);
        analysisScrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
        analyzeButton.addActionListener(e -> {
            String analysisResult = analyzeAttendance();
            analysisTextArea.setText(analysisResult);
        });
        JPanel analyzePanel = new JPanel();
        analyzePanel.setBackground(Color.WHITE);
        analyzePanel.add(analyzeButton);
        analyzeAttendancePanel.add(analyzePanel, BorderLayout.NORTH);
        analyzeAttendancePanel.add(analysisScrollPane, BorderLayout.CENTER);
        tabbedPane.addTab("Attendance Analysis", null, analyzeAttendancePanel, "Attendance Analysis");

        // Add components to the frame
        add(controlPanel, BorderLayout.NORTH);
        add(tabbedPane, BorderLayout.CENTER);

        // Set frame properties
        setSize(600, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Connect to server
        try {
            socket = new Socket(SERVER_IP, SERVER_PORT);
            dos = new DataOutputStream(socket.getOutputStream());
        } catch (IOException ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Failed to connect to server", "Connection Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void sendCommand(String command) {
        try {
            dos.write((command + "\n").getBytes());
            dos.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void readCSV(String filePath) {
        File file = new File(filePath);
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String line;
            String[] headers = br.readLine().split(",");
            tableModel = new DefaultTableModel(headers, 0);
            while ((line = br.readLine()) != null) {
                String[] rowData = line.split(",");
                tableModel.addRow(rowData);
            }
            table = new JTable(tableModel);
            table.setBackground(Color.WHITE);
            table.getTableHeader().setBackground(Color.decode("#BBDEFB"));
            JScrollPane scrollPane = new JScrollPane(table);
            tablePanel.removeAll();
            tablePanel.add(scrollPane, BorderLayout.CENTER);
            tablePanel.revalidate();
            tablePanel.repaint();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void refreshTable(String filePath) {
        if (tableModel != null) {
            tableModel.setRowCount(0); // Clear previous data
        }
        readCSV(filePath); // Reload table data
    }

    private void clearAttendanceFile(String filePath) {
        File file = new File(filePath);
        File tempFile = new File(file.getAbsolutePath()+ ".tmp");
        try (BufferedReader br = new BufferedReader(new FileReader(file));
             PrintWriter pw = new PrintWriter(new FileWriter(tempFile))) {
            String firstLine = br.readLine(); // Read and keep the first line
            pw.println(firstLine); // Write the first line to the temp file
        } catch (IOException e) {
            e.printStackTrace();
        }
        // Delete the original file
        if (!file.delete()) {
            System.out.println("Could not delete file");
            return;
        }
        // Rename the new file to the filename the original file had.
        if (!tempFile.renameTo(file))
            System.out.println("Could not rename file");

        refreshTable(filePath); // Refresh table after clearing file
    }

    private void saveAttendance(String fileName) {
        Path source = Paths.get(defaultFilePath);
        Path destination = Paths.get("C:\\Users\\hp\\Documents\\Java\\JavaFx project\\Attendance\\" + fileName + ".csv");
        try {
            Files.copy(source, destination, StandardCopyOption.REPLACE_EXISTING);
            JOptionPane.showMessageDialog(this, "Attendance saved successfully.", "Success", JOptionPane.INFORMATION_MESSAGE);
        } catch (IOException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(this, "Failed to save attendance.", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private String analyzeAttendance() {
        StringBuilder analysisResult = new StringBuilder();

        // Define the directory where attendance files are stored
        String directoryPath = "C:\\Users\\hp\\Documents\\Java\\JavaFx project\\Attendance\\";

        // Read all files in the directory
        File directory = new File(directoryPath);
        File[] files = directory.listFiles();

        if (files != null && files.length > 0) {
            for (File file : files) {
                // Process each file
                if (file.isFile()) {
                    // Analyze the file
                    String fileName = file.getName();
                    analysisResult.append("File/Day: ").append(fileName).append("\n");

                    try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                        // Skip the header line
                        br.readLine();

                        // Count attendance for each day
                        int totalLines = 0;
                        int presentCount = 0;
                        int absentCount = 0;
                        String line;
                        while ((line = br.readLine()) != null) {
                            totalLines++;
                            String[] columns = line.split(",");
                            String status = columns[1]; // Assuming status is in the second column
                            if (status.equalsIgnoreCase("Present")) {
                                presentCount++;
                            } else {
                                absentCount++;
                            }
                        }
                        presentCount = totalLines;

                        int total_students = 10;
                        absentCount = total_students - presentCount;
                        // Calculate percentage
                        double presentPercentage = ((double) totalLines / total_students) * 100;
                        double absentPercentage = ((double) (total_students-totalLines) / total_students) * 100;

                        // Append analysis to result
//                        analysisResult.append("Total Students: ").append(totalLines).append("\n");
                        analysisResult.append("Present: ").append(presentCount).append(" (").append(String.format("%.2f", presentPercentage)).append("%)\n");
                        analysisResult.append("Absent: ").append(absentCount).append(" (").append(String.format("%.2f", absentPercentage)).append("%)\n\n");

                    } catch (IOException e) {
                        e.printStackTrace();
                        analysisResult.append("Error reading file: ").append(fileName).append("\n\n");
                    }
                }
            }
        } else {
            analysisResult.append("No attendance files found.\n");
        }

        return analysisResult.toString();
    }




    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new v1().setVisible(true));
    }
}
