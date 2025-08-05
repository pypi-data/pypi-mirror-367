using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

[McpServerToolType]
public static class ScreenshotTool
{
    // Windows API für Screenshot-Funktionalität
    [DllImport("user32.dll")]
    private static extern int GetSystemMetrics(int nIndex);

    private const int SM_CXSCREEN = 0;           // Primärer Bildschirm Breite
    private const int SM_CYSCREEN = 1;           // Primärer Bildschirm Höhe  
    private const int SM_XVIRTUALSCREEN = 76;    // Virtueller Desktop X
    private const int SM_YVIRTUALSCREEN = 77;    // Virtueller Desktop Y
    private const int SM_CXVIRTUALSCREEN = 78;   // Virtueller Desktop Breite
    private const int SM_CYVIRTUALSCREEN = 79;   // Virtueller Desktop Höhe

    [McpServerTool, Description("Macht einen Screenshot aller Bildschirme (simuliert Print Screen)")]
    public static string TakeScreenshot()
    {
        try
        {
            // Hole virtuelle Desktop-Dimensionen (alle Bildschirme)
            int x = GetSystemMetrics(SM_XVIRTUALSCREEN);
            int y = GetSystemMetrics(SM_YVIRTUALSCREEN);
            int width = GetSystemMetrics(SM_CXVIRTUALSCREEN);
            int height = GetSystemMetrics(SM_CYVIRTUALSCREEN);

            // Screenshot erstellen
            using var bitmap = new Bitmap(width, height);
            using var graphics = Graphics.FromImage(bitmap);
            
            graphics.CopyFromScreen(x, y, 0, 0, new Size(width, height));

            // Speichere im aktuellen Workspace (für Copilot-Zugriff)
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss");
            string filename = $"screenshot_{timestamp}.png";
            
            // Bestimme aktuelles Arbeitsverzeichnis (VS Code Workspace)
            string workspaceDir = Directory.GetCurrentDirectory();
            string filepath = Path.Combine(workspaceDir, filename);
            
            bitmap.Save(filepath, ImageFormat.Png);

            return $"✅ Screenshot aller Bildschirme erfolgreich gespeichert!\n📁 Pfad: {filepath}\n📐 Größe: {width}x{height} Pixel\n🖥️ Virtueller Desktop von ({x},{y}) erfasst\n💡 Hinweis: Screenshot wurde im aktuellen Workspace gespeichert";
        }
        catch (Exception ex)
        {
            return $"❌ Fehler beim Screenshot aller Bildschirme: {ex.Message}";
        }
    }

    [McpServerTool, Description("Macht einen Screenshot nur vom primären Bildschirm")]
    public static string TakePrimaryScreenshot()
    {
        try
        {
            // Primärer Bildschirm
            int width = GetSystemMetrics(SM_CXSCREEN);
            int height = GetSystemMetrics(SM_CYSCREEN);

            using var bitmap = new Bitmap(width, height);
            using var graphics = Graphics.FromImage(bitmap);
            
            graphics.CopyFromScreen(0, 0, 0, 0, new Size(width, height));

            string timestamp = DateTime.Now.ToString("yyyy-MM-dd_HH-mm-ss");
            string filename = $"primary_screenshot_{timestamp}.png";
            
            // Bestimme Workspace-Verzeichnis (VS Code arbeitet normalerweise hier)
            string workspaceDir = Directory.GetCurrentDirectory();
            
            // Falls wir nicht im gewünschten Workspace sind, verwende das Verzeichnis des aktuellen Prozesses
            if (!Directory.Exists(Path.Combine(workspaceDir, ".vscode")) && 
                !File.Exists(Path.Combine(workspaceDir, "package.json")) &&
                !File.Exists(Path.Combine(workspaceDir, "*.sln")) &&
                !File.Exists(Path.Combine(workspaceDir, "*.csproj")))
            {
                // Fallback: Verwende das Verzeichnis, in dem der MCP Server liegt
                workspaceDir = Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) ?? workspaceDir;
            }
            
            string filepath = Path.Combine(workspaceDir, filename);
            
            bitmap.Save(filepath, ImageFormat.Png);

            return $"✅ Primärer Bildschirm-Screenshot erfolgreich gespeichert!\n📁 Pfad: {filepath}\n📐 Größe: {width}x{height} Pixel\n💡 Hinweis: Screenshot wurde im aktuellen Workspace gespeichert";
        }
        catch (Exception ex)
        {
            return $"❌ Fehler beim primären Screenshot: {ex.Message}";
        }
    }

    [McpServerTool, Description("Zeigt Informationen über alle verfügbaren Bildschirme")]
    public static string GetScreenInfo()
    {
        try
        {
            int primaryWidth = GetSystemMetrics(SM_CXSCREEN);
            int primaryHeight = GetSystemMetrics(SM_CYSCREEN);
            int virtualX = GetSystemMetrics(SM_XVIRTUALSCREEN);
            int virtualY = GetSystemMetrics(SM_YVIRTUALSCREEN);
            int virtualWidth = GetSystemMetrics(SM_CXVIRTUALSCREEN);
            int virtualHeight = GetSystemMetrics(SM_CYVIRTUALSCREEN);

            var info = new List<string>
            {
                "🖥️ Bildschirm-Informationen:",
                "",
                $"🎯 Primärer Bildschirm: {primaryWidth}x{primaryHeight} Pixel",
                $"🌐 Virtueller Desktop: {virtualWidth}x{virtualHeight} Pixel",
                $"📍 Virtual Desktop Position: ({virtualX}, {virtualY})",
                "",
                "💡 Hinweis: 'TakeScreenshot' erfasst alle Bildschirme (Print Screen simuliert)",
                "💡 Hinweis: 'TakePrimaryScreenshot' erfasst nur den Hauptbildschirm"
            };

            return string.Join("\n", info);
        }
        catch (Exception ex)
        {
            return $"❌ Fehler beim Abrufen der Bildschirm-Informationen: {ex.Message}";
        }
    }

    [McpServerTool, Description("Emuliert den Windows Print Screen Tastendruck")]
    public static string SimulatePrintScreen()
    {
        // Dies ist das gleiche wie TakeScreenshot, aber mit expliziter Print Screen Bezeichnung
        return TakeScreenshot();
    }
}
