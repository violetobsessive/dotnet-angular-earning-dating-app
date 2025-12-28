using Microsoft.EntityFrameworkCore.Metadata.Internal;

namespace API.Entities;

public class AppUser
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public required string DisplayName { get; set; }
    public required string Email { get; set; }
    
    // Add security to user passwords

    // Encrpt password to hash
    public required byte[] PasswordHash { get; set; }
    
    // Add random generated salt to hash
    public required byte[] PasswordSalt { get; set; }
}