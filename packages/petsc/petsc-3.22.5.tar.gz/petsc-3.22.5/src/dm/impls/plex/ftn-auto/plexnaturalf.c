#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexnatural.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetmigrationsf_ DMPLEXSETMIGRATIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetmigrationsf_ dmplexsetmigrationsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetmigrationsf_ DMPLEXGETMIGRATIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetmigrationsf_ dmplexgetmigrationsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetglobaltonaturalsf_ DMPLEXSETGLOBALTONATURALSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetglobaltonaturalsf_ dmplexsetglobaltonaturalsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetglobaltonaturalsf_ DMPLEXGETGLOBALTONATURALSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetglobaltonaturalsf_ dmplexgetglobaltonaturalsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateglobaltonaturalsf_ DMPLEXCREATEGLOBALTONATURALSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateglobaltonaturalsf_ dmplexcreateglobaltonaturalsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexmigrateglobaltonaturalsf_ DMPLEXMIGRATEGLOBALTONATURALSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexmigrateglobaltonaturalsf_ dmplexmigrateglobaltonaturalsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexglobaltonaturalbegin_ DMPLEXGLOBALTONATURALBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexglobaltonaturalbegin_ dmplexglobaltonaturalbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexglobaltonaturalend_ DMPLEXGLOBALTONATURALEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexglobaltonaturalend_ dmplexglobaltonaturalend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexnaturaltoglobalbegin_ DMPLEXNATURALTOGLOBALBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexnaturaltoglobalbegin_ dmplexnaturaltoglobalbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexnaturaltoglobalend_ DMPLEXNATURALTOGLOBALEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexnaturaltoglobalend_ dmplexnaturaltoglobalend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatenaturalvector_ DMPLEXCREATENATURALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatenaturalvector_ dmplexcreatenaturalvector
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexsetmigrationsf_(DM dm,PetscSF migrationSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(migrationSF);
*ierr = DMPlexSetMigrationSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((migrationSF) ));
}
PETSC_EXTERN void  dmplexgetmigrationsf_(DM dm,PetscSF *migrationSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool migrationSF_null = !*(void**) migrationSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(migrationSF);
*ierr = DMPlexGetMigrationSF(
	(DM)PetscToPointer((dm) ),migrationSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! migrationSF_null && !*(void**) migrationSF) * (void **) migrationSF = (void *)-2;
}
PETSC_EXTERN void  dmplexsetglobaltonaturalsf_(DM dm,PetscSF naturalSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(naturalSF);
*ierr = DMPlexSetGlobalToNaturalSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((naturalSF) ));
}
PETSC_EXTERN void  dmplexgetglobaltonaturalsf_(DM dm,PetscSF *naturalSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool naturalSF_null = !*(void**) naturalSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(naturalSF);
*ierr = DMPlexGetGlobalToNaturalSF(
	(DM)PetscToPointer((dm) ),naturalSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! naturalSF_null && !*(void**) naturalSF) * (void **) naturalSF = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateglobaltonaturalsf_(DM dm,PetscSection section,PetscSF sfMigration,PetscSF *sfNatural, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(section);
CHKFORTRANNULLOBJECT(sfMigration);
PetscBool sfNatural_null = !*(void**) sfNatural ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfNatural);
*ierr = DMPlexCreateGlobalToNaturalSF(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((section) ),
	(PetscSF)PetscToPointer((sfMigration) ),sfNatural);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfNatural_null && !*(void**) sfNatural) * (void **) sfNatural = (void *)-2;
}
PETSC_EXTERN void  dmplexmigrateglobaltonaturalsf_(DM dmOld,DM dmNew,PetscSF sfNaturalOld,PetscSF sfMigration,PetscSF *sfNaturalNew, int *ierr)
{
CHKFORTRANNULLOBJECT(dmOld);
CHKFORTRANNULLOBJECT(dmNew);
CHKFORTRANNULLOBJECT(sfNaturalOld);
CHKFORTRANNULLOBJECT(sfMigration);
PetscBool sfNaturalNew_null = !*(void**) sfNaturalNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfNaturalNew);
*ierr = DMPlexMigrateGlobalToNaturalSF(
	(DM)PetscToPointer((dmOld) ),
	(DM)PetscToPointer((dmNew) ),
	(PetscSF)PetscToPointer((sfNaturalOld) ),
	(PetscSF)PetscToPointer((sfMigration) ),sfNaturalNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfNaturalNew_null && !*(void**) sfNaturalNew) * (void **) sfNaturalNew = (void *)-2;
}
PETSC_EXTERN void  dmplexglobaltonaturalbegin_(DM dm,Vec gv,Vec nv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(gv);
CHKFORTRANNULLOBJECT(nv);
*ierr = DMPlexGlobalToNaturalBegin(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((gv) ),
	(Vec)PetscToPointer((nv) ));
}
PETSC_EXTERN void  dmplexglobaltonaturalend_(DM dm,Vec gv,Vec nv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(gv);
CHKFORTRANNULLOBJECT(nv);
*ierr = DMPlexGlobalToNaturalEnd(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((gv) ),
	(Vec)PetscToPointer((nv) ));
}
PETSC_EXTERN void  dmplexnaturaltoglobalbegin_(DM dm,Vec nv,Vec gv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(nv);
CHKFORTRANNULLOBJECT(gv);
*ierr = DMPlexNaturalToGlobalBegin(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((nv) ),
	(Vec)PetscToPointer((gv) ));
}
PETSC_EXTERN void  dmplexnaturaltoglobalend_(DM dm,Vec nv,Vec gv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(nv);
CHKFORTRANNULLOBJECT(gv);
*ierr = DMPlexNaturalToGlobalEnd(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((nv) ),
	(Vec)PetscToPointer((gv) ));
}
PETSC_EXTERN void  dmplexcreatenaturalvector_(DM dm,Vec *nv, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool nv_null = !*(void**) nv ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nv);
*ierr = DMPlexCreateNaturalVector(
	(DM)PetscToPointer((dm) ),nv);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nv_null && !*(void**) nv) * (void **) nv = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
