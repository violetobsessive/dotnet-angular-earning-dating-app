using System;
using System.Security.Cryptography;
using System.Text;
using API.Data;
using API.DTOs;
using API.Entities;
using API.Interfaces;
using API.Servicces;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace API.Controllers;

public class AccountController(AppDbContext context, ITokenService tokenService) : BaseApiController
{
    [HttpPost("register")] //api/account/register
    public async Task<ActionResult<UserDto>>Register(RegisterDto registerDto)
    {
        if(await EmailExists(registerDto.Email)) return BadRequest("Email already exists!");
        // hash password
        using var hmac = new HMACSHA512();
        
        var user = new AppUser
        {
            DisplayName = registerDto.DisplayName,
            Email = registerDto.Email,
            PasswordHash = hmac.ComputeHash(Encoding.UTF8.GetBytes(registerDto.Password)),
            PasswordSalt = hmac.Key
        };

        // Add user to DB
        context.Users.Add(user);
        await context.SaveChangesAsync();

        return new UserDto
        {
            Id = user.Id,
            DisplayName = user.DisplayName,
            Email = user.Email,
            Token = tokenService.CreateToken(user)
        };
    }
    // Helper method to see if an email address already exists
    private async Task<bool> EmailExists(string email)
    {
        return await context.Users.AnyAsync(x => x.Email.ToLower() == email.ToLower());
    }

    [HttpPost("login")]
    public async Task<ActionResult<UserDto>> Login(LoginDto loginDto)
    {
        var user = await context.Users.SingleOrDefaultAsync(x => x.Email == loginDto.Email);
        
        if(user == null) return Unauthorized("Invalid email address!");
        
        // Compare the hashed version from DB with hashed version passed in from password in loginDto
        // Supply password salt, so it creates same key to create hashed password
        using var hmac = new HMACSHA512(user.PasswordSalt);
        var compustedHash = hmac.ComputeHash(Encoding.UTF8.GetBytes(loginDto.Password));
        for(var i = 0; i < compustedHash.Length; i++)
        {
            if(compustedHash[i] != user.PasswordHash[i]) return Unauthorized("Invalid password!");
        }
        return new UserDto
        {
            Id = user.Id,
            DisplayName = user.DisplayName,
            Email = user.Email,
            Token = tokenService.CreateToken(user)
        };
    }
}
