using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using API.Entities;
using API.Interfaces;
using Microsoft.IdentityModel.Tokens;

namespace API.Servicces;

public class TokenService(IConfiguration config):ITokenService
{
    public string CreateToken(AppUser user)
    {
        var tokenKey = config["TokenKey"] ?? throw new Exception("Cannot get token key");
        if(tokenKey.Length < 64) 
            throw new Exception("Token needs to be >= 64 characters");
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(tokenKey));

        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.NameIdentifier, user.Id)
        };
        // holds key from SymmetricSecurityKey and algorithm
        // JWT third part signature is computed using these credentials
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha512Signature);
        
        var issuer = config["Jwt:Issuer"];
        var audience = config["Jwt:Audience"];
        
        //a blueprint/config object describing what to put into the token
        var tokenDescriptor = new SecurityTokenDescriptor
        {
            // Identity/claims that become the token payload
            Subject = new ClaimsIdentity(claims),
            Expires = DateTime.UtcNow.AddDays(7),
            
            Issuer = issuer,               
            Audience = audience,
            
            // How it should be signed
            SigningCredentials = credentials
        };
        // Component that creates and writes/reads JWTs
        var tokenHandler = new JwtSecurityTokenHandler();
        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);
    }
}